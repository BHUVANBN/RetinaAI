# Quick Start Guide

## 🚀 Running the Application

### Option 1: Development Server
```bash
cd /home/batman/Diabetic-Retinopathy/DR_refined
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Option 2: Docker Deployment
```bash
cd /home/batman/Diabetic-Retinopathy/DR_refined
docker-compose up --build
```

## 🌐 Access Points

- **Main Application**: http://localhost:8000/prediction/
- **Health Check**: http://localhost:8000/prediction/health/
- **Model Info**: http://localhost:8000/prediction/model-info/
- **Admin Panel**: http://localhost:8000/admin/

## 🧪 Testing the API

### Test Image Upload
```bash
# Using curl
curl -X POST -F "image=@your_image.jpg" http://localhost:8000/prediction/predict/

# Response example
{
    "prediction": "Moderate",
    "confidence": 34.23,
    "all_probabilities": [23.77, 14.28, 34.23, 14.99, 12.74],
    "success": true,
    "demo_mode": true,
    "graph_url": "/media/graphs/prediction_graph.png"
}
```

### Health Check
```bash
curl http://localhost:8000/prediction/health/
# Response: {"status": "healthy", "model_loaded": false, "demo_mode": true}
```

## 📊 Current Status

✅ **Application**: Running successfully  
✅ **API Endpoints**: Working  
✅ **UI**: Modern, responsive design  
✅ **Error Handling**: Comprehensive with demo mode  
⚠️ **Model**: Running in demo mode (TensorFlow compatibility issue)  

## 🔧 Features Working

- **Image Upload & Processing**: ✅
- **Prediction API**: ✅ (demo mode)
- **Probability Distribution**: ✅
- **Graph Generation**: ✅
- **Modern UI**: ✅
- **Health Monitoring**: ✅
- **File Validation**: ✅
- **Error Handling**: ✅

## 🎯 Next Steps

1. **Fix TensorFlow Compatibility**: Update model loading for newer TensorFlow versions
2. **Add Real Test Images**: Place retinal fundus images in test directory
3. **Production Deployment**: Configure SSL and domain settings
4. **Performance Optimization**: Add caching and connection pooling

## 📱 UI Features

- **Drag & Drop** image upload
- **Real-time** analysis with loading states
- **Interactive** probability charts
- **Responsive** design for all devices
- **Modern** Tailwind CSS styling
- **Accessibility** features

## 🐛 Troubleshooting

### Model Loading Issues
The application currently runs in demo mode due to TensorFlow version compatibility. The model needs to be re-saved with a compatible TensorFlow version.

### File Upload Issues
- Max file size: 10MB
- Supported formats: JPG, PNG, JPEG
- Images are automatically resized to 224×224

### Performance Issues
- Enable GPU support for TensorFlow
- Use production deployment with Nginx
- Implement Redis caching for repeated requests
