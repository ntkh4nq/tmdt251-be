import cloudinary.uploader
from fastapi import UploadFile, HTTPException
from typing import Optional
import os

class CloudinaryService:
    
    @staticmethod
    async def upload_image(
        file: UploadFile,
        folder: str = "products"
    ) -> dict:
        """
        Upload ảnh lên Cloudinary
        
        Args:
            file: File upload từ FastAPI
            folder: Thư mục trên Cloudinary (vd: products, categories)
        
        Returns:
            dict với url, public_id, width, height, format
        """
        try:
            # Validate file type
            allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {file.content_type} not allowed. Only JPEG, PNG, WEBP"
                )
            
            # Validate file size (max 5MB)
            file.file.seek(0, os.SEEK_END)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > 5 * 1024 * 1024:  # 5MB
                raise HTTPException(
                    status_code=400,
                    detail="File size exceeds 5MB"
                )
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file.file,
                folder=folder,
                resource_type="image",
                transformation=[
                    {"width": 1000, "height": 1000, "crop": "limit"},
                    {"quality": "auto:good"}
                ]
            )
            
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"]
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    @staticmethod
    async def delete_image(public_id: str) -> bool:
        """
        Xóa ảnh từ Cloudinary
        
        Args:
            public_id: ID của ảnh trên Cloudinary
        
        Returns:
            True nếu xóa thành công
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
        except Exception as e:
            print(f"Delete failed: {str(e)}")
            return False