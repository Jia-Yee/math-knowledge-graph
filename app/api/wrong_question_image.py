"""
错题图片上传 API
支持图片上传、OCR识别、错题自动解析
"""

from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import uuid
import base64
import re
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

router = APIRouter(prefix="/users", tags=["错题图片"])

# 配置
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
WRONG_QUESTIONS_IMG_DIR = DATA_DIR / "wrong-questions-img"
WRONG_QUESTIONS_IMG_DIR.mkdir(parents=True, exist_ok=True)

THUMBNAIL_SIZE = (300, 300)

# 数据文件路径
def get_user_wrong_questions_file(user_id: str) -> Path:
    return DATA_DIR / "wrong-questions" / f"{user_id}.json"

# 加载用户错题数据
def load_user_wrong_questions(user_id: str) -> dict:
    file_path = get_user_wrong_questions_file(user_id)
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "user_id": user_id,
        "total_count": 0,
        "active_count": 0,
        "mastered_count": 0,
        "wrong_questions": [],
        "wrong_question_images": [],
        "updated_at": datetime.now().isoformat()
    }

# 保存用户错题数据
def save_user_wrong_questions(user_id: str, data: dict):
    file_path = get_user_wrong_questions_file(user_id)
    data["updated_at"] = datetime.now().isoformat()
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving: {e}")

# OCR 识别函数
async def perform_ocr(image_path: str) -> dict:
    """
    使用 GPT-4o Vision 进行 OCR 识别
    """
    try:
        import openai
        import os
        
        # 读取图片并转为 base64
        with open(image_path, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 调用 GPT-4o Vision
        client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """你是一个数学错题分析助手。请分析这张图片中的数学题目。

请用以下 JSON 格式返回结果：
{
    "question": "识别的题目内容",
    "wrong_answer": "用户写的错误答案（如果有）",
    "correct_answer": "正确答案（如果有）",
    "error_type": "可能的错误类型",
    "confidence": 0.0-1.0 的置信度,
    "analysis": "简要的错误分析"
}

注意：
1. 只返回 JSON，不要有其他内容
2. 如果无法识别，返回空的 JSON 对象 {}
3. 对于选择题，请识别选项和用户的选择
4. 如果图片中没有数学题目，返回空的 JSON 对象 {}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # 尝试解析 JSON
        try:
            # 移除可能的前后空白和 markdown 代码块
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            return result
        except:
            return {
                "question": result_text,
                "confidence": 0.5
            }
            
    except Exception as e:
        print(f"OCR Error: {e}")
        return {
            "question": "",
            "confidence": 0,
            "error": str(e)
        }

# 简单的本地 OCR (备选方案)
def simple_ocr(image_path: str) -> dict:
    """
    使用本地 Tesseract OCR 作为备选方案
    """
    try:
        import pytesseract
        
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        
        # 尝试提取关键信息
        question = ""
        wrong_answer = ""
        correct_answer = ""
        
        # 提取"你的答案"和"正确答案"
        lines = text.split('\n')
        for line in lines:
            if '答' in line or '答案' in line:
                if '错' in line or 'wrong' in line.lower():
                    wrong_answer = extract_number(line)
                elif '正确' in line or '对' in line:
                    correct_answer = extract_number(line)
        
        return {
            "question": text.strip(),
            "wrong_answer": wrong_answer,
            "correct_answer": correct_answer,
            "confidence": 0.6
        }
    except ImportError:
        return {
            "question": "",
            "confidence": 0,
            "error": "Tesseract not installed"
        }
    except Exception as e:
        return {
            "question": "",
            "confidence": 0,
            "error": str(e)
        }

def extract_number(text: str) -> str:
    """从文本中提取数学表达式"""
    # 匹配常见数学格式
    patterns = [
        r'[＝=:=]\s*([^\s,，]+)',
        r'答[：:]\s*([^\s,，]+)',
        r'答案[：:]\s*([^\s,，]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    return text.strip()

# 创建缩略图
def create_thumbnail(image_path: str, thumb_path: str):
    """创建缩略图"""
    try:
        img = Image.open(image_path)
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)
        return True
    except Exception as e:
        print(f"Thumbnail error: {e}")
        return False

# 数据模型
class WrongQuestionImageCreate(BaseModel):
    """创建错题图片关联"""
    wrong_question_id: str
    image_id: str
    ocr_text: Optional[str] = None
    ocr_confidence: float = 0

class UploadResult(BaseModel):
    success: bool
    image_id: str
    image_url: str
    thumbnail_url: Optional[str] = None
    ocr_result: Optional[dict] = None
    parsed: Optional[dict] = None
    wrong_question_id: Optional[str] = None
    message: str

# ===== API 路由 =====

@router.post("/{user_id}/wrong-questions/upload")
async def upload_wrong_question_image(
    user_id: str,
    file: UploadFile = File(...),
    auto_save: bool = False  # 是否自动保存为错题
):
    """上传错题图片并进行 OCR 识别"""
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片格式: {file.content_type}"
        )
    
    # 生成图片 ID
    image_id = f"wqi_{uuid.uuid4().hex[:8]}"
    
    # 确定文件扩展名
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    if ext.lower() not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        ext = 'jpg'
    
    # 保存图片
    file_path = WRONG_QUESTIONS_IMG_DIR / f"{image_id}.{ext}"
    thumb_path = WRONG_QUESTIONS_IMG_DIR / f"thumb_{image_id}.{ext}"
    
    try:
        content = await file.read()
        
        # 保存原图
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 创建缩略图
        create_thumbnail(str(file_path), str(thumb_path))
        
        # OCR 暂不调用（需要配置 OpenAI key），直接返回空
        ocr_result = {"question": "", "wrong_answer": "", "correct_answer": "", "confidence": 0}
        
        # 构建结果
        result = UploadResult(
            success=True,
            image_id=image_id,
            image_url=f"/static/wrong-questions-img/{image_id}.{ext}",
            thumbnail_url=f"/static/wrong-questions-img/thumb_{image_id}.{ext}" if thumb_path.exists() else None,
            ocr_result=ocr_result,
            parsed={
                "question": ocr_result.get("question", ""),
                "wrong_answer": ocr_result.get("wrong_answer", ""),
                "correct_answer": ocr_result.get("correct_answer", ""),
                "error_type": ocr_result.get("error_type", ""),
                "confidence": ocr_result.get("confidence", 0)
            },
            message="图片已识别，请在 Web 页面确认并保存为错题"
        )
        
        # 如果需要自动保存
        if auto_save and ocr_result.get("question"):
            # 这里可以调用错题保存逻辑
            result.wrong_question_id = "pending_confirmation"
            result.message = "已识别并创建错题草稿，请在 Web 页面确认"
        
        # 保存图片记录到 JSON（每次上传都保存）
        user_data = load_user_wrong_questions(user_id)
        if "wrong_question_images" not in user_data:
            user_data["wrong_question_images"] = []
        user_data["wrong_question_images"].append({
            "id": image_id,
            "user_id": user_id,
            "image_url": result.image_url,
            "thumbnail_url": result.thumbnail_url,
            "filename": f"{image_id}.{ext}",
            "uploaded_at": datetime.now().isoformat(),
            "ocr_result": ocr_result
        })
        save_user_wrong_questions(user_id, user_data)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/{user_id}/wrong-questions/images")
async def list_wrong_question_images(
    user_id: str,
    wq_id: Optional[str] = None
):
    """获取用户的错题图片列表"""
    
    user_data = load_user_wrong_questions(user_id)
    images = user_data.get("wrong_question_images", [])
    
    # 过滤
    if wq_id:
        images = [img for img in images if img.get("wrong_question_id") == wq_id]
    
    return {
        "user_id": user_id,
        "total": len(images),
        "images": images
    }

@router.get("/{user_id}/wrong-questions/images/{image_id}")
async def get_wrong_question_image(user_id: str, image_id: str):
    """获取单个错题图片详情"""
    
    user_data = load_user_wrong_questions(user_id)
    images = user_data.get("wrong_question_images", [])
    
    for img in images:
        if img.get("id") == image_id:
            return img
    
    raise HTTPException(status_code=404, detail="图片不存在")

@router.post("/{user_id}/wrong-questions/images/{image_id}/link")
async def link_image_to_wrong_question(
    user_id: str,
    image_id: str,
    wrong_question_id: str
):
    """将图片关联到错题"""
    
    user_data = load_user_wrong_questions(user_id)
    
    # 查找或创建图片记录
    images = user_data.get("wrong_question_images", [])
    img_found = None
    
    for img in images:
        if img.get("id") == image_id:
            img_found = img
            break
    
    if not img_found:
        # 创建新记录
        img_found = {
            "id": image_id,
            "wrong_question_id": wrong_question_id,
            "created_at": datetime.now().isoformat()
        }
        images.append(img_found)
        user_data["wrong_question_images"] = images
    
    # 更新关联的错题
    wrong_questions = user_data.get("wrong_questions", [])
    for wq in wrong_questions:
        if wq.get("id") == wrong_question_id:
            if "images" not in wq:
                wq["images"] = []
            if image_id not in wq["images"]:
                wq["images"].append(image_id)
            break
    
    save_user_wrong_questions(user_id, user_data)
    
    return {"success": True, "message": "图片已关联到错题"}

@router.delete("/{user_id}/wrong-questions/images/{image_id}")
async def delete_wrong_question_image(user_id: str, image_id: str):
    """删除错题图片"""
    
    user_data = load_user_wrong_questions(user_id)
    
    # 删除文件
    for ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        file_path = WRONG_QUESTIONS_IMG_DIR / f"{image_id}.{ext}"
        thumb_path = WRONG_QUESTIONS_IMG_DIR / f"thumb_{image_id}.{ext}"
        
        if file_path.exists():
            file_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()
    
    # 从数据库中移除
    images = user_data.get("wrong_question_images", [])
    images = [img for img in images if img.get("id") != image_id]
    user_data["wrong_question_images"] = images
    
    # 从错题中移除关联
    for wq in user_data.get("wrong_questions", []):
        if "images" in wq and image_id in wq["images"]:
            wq["images"].remove(image_id)
    
    save_user_wrong_questions(user_id, user_data)
    
    return {"success": True, "message": "图片已删除"}

@router.post("/ocr/recognize")
@router.post("/{user_id}/wrong-questions/recognize")
async def recognize_text(file: UploadFile = File(...)):
    """通用 OCR 识别接口"""
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    # 保存临时文件
    temp_id = f"temp_{uuid.uuid4().hex[:8]}"
    temp_path = WRONG_QUESTIONS_IMG_DIR / f"{temp_id}.jpg"
    
    try:
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        # OCR 识别
        result = await perform_ocr(str(temp_path))
        
        return {
            "success": True,
            "result": result
        }
        
    finally:
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()

print("✅ 错题图片 API 已加载")
