<template>
  <div class="image-upload-container">
    <div class="upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
      <div v-if="!imagePreview" class="upload-placeholder">
        <div class="upload-icon">📷</div>
        <p>点击或拖拽上传图片</p>
        <p class="upload-hint">支持 PNG, JPG, JPEG, GIF, BMP, WEBP 格式</p>
      </div>
      <div v-else class="image-preview">
        <img :src="imagePreview" alt="预览图片" class="preview-image" />
        <div class="image-overlay">
          <button @click.stop="removeImage" class="remove-btn">删除</button>
          <button @click.stop="triggerFileInput" class="change-btn">更换</button>
        </div>
      </div>
    </div>
    
    <input 
      ref="fileInput" 
      type="file" 
      accept="image/*" 
      @change="handleFileSelect" 
      style="display: none"
    />
    
    <div v-if="uploading" class="upload-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
      <p>上传中... {{ uploadProgress }}%</p>
    </div>
    
    <div v-if="uploadError" class="error-message">
      {{ uploadError }}
    </div>
    
    <div v-if="uploadSuccess" class="success-message">
      图片上传成功！
    </div>
  </div>
</template>

<script setup>
import { ref, defineEmits, defineProps } from 'vue'
import { flaskApiService } from '../axios' // 修改为命名导入

const props = defineProps({
  carId: {
    type: Number,
    default: null
  },
  initialImage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['upload-success', 'upload-error'])

const fileInput = ref(null)
const imagePreview = ref(props.initialImage)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadError = ref('')
const uploadSuccess = ref(false)
const selectedFile = ref(null)

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    validateAndPreviewFile(file)
  }
}

const handleDrop = (event) => {
  const files = event.dataTransfer.files
  if (files.length > 0) {
    validateAndPreviewFile(files[0])
  }
}

const validateAndPreviewFile = (file) => {
  // 验证文件类型
  const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/bmp', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    uploadError.value = '不支持的文件类型，请选择图片文件'
    return
  }
  
  // 验证文件大小（10MB限制）
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    uploadError.value = '文件大小不能超过10MB'
    return
  }
  
  // 清除之前的错误信息
  uploadError.value = ''
  uploadSuccess.value = false
  selectedFile.value = file
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)
  
  // 自动上传
  uploadFile()
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  uploading.value = true
  uploadProgress.value = 0
  uploadError.value = ''
  uploadSuccess.value = false
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await axios.post('/api/upload_car_image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        uploadProgress.value = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        )
      }
    })
    
    if (response.data.success) {
      uploadSuccess.value = true
      
      // 如果提供了车辆ID，更新车辆图片
      if (props.carId) {
        await updateCarImage(response.data.object_name)
      }
      
      emit('upload-success', {
        objectName: response.data.object_name,
        fileUrl: response.data.file_url
      })
    } else {
      throw new Error(response.data.error || '上传失败')
    }
  } catch (error) {
    uploadError.value = error.response?.data?.error || error.message || '上传失败'
    emit('upload-error', uploadError.value)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
  }
}

const updateCarImage = async (objectName) => {
  try {
    const response = await axios.post('/api/update_car_image', {
      car_id: props.carId,
      image_object_name: objectName
    })
    
    if (!response.data.success) {
      throw new Error(response.data.error || '更新车辆图片失败')
    }
  } catch (error) {
    console.error('更新车辆图片失败:', error)
    uploadError.value = '图片上传成功，但更新车辆信息失败'
  }
}

const removeImage = () => {
  imagePreview.value = ''
  selectedFile.value = null
  uploadError.value = ''
  uploadSuccess.value = false
  
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}
</script>

<style scoped>
.image-upload-container {
  max-width: 400px;
  margin: 0 auto;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s ease;
  position: relative;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #007bff;
}

.upload-placeholder {
  color: #666;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.upload-hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.image-preview {
  position: relative;
  width: 100%;
  height: 200px;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.remove-btn, .change-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.remove-btn {
  background-color: #dc3545;
  color: white;
}

.remove-btn:hover {
  background-color: #c82333;
}

.change-btn {
  background-color: #007bff;
  color: white;
}

.change-btn:hover {
  background-color: #0056b3;
}

.upload-progress {
  margin-top: 15px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  background-color: #007bff;
  transition: width 0.3s ease;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
}

.success-message {
  color: #155724;
  font-size: 14px;
  margin-top: 10px;
  padding: 8px;
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  border-radius: 4px;
}
</style>