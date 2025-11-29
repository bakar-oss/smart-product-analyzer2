from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SmartProductAnalyzer:
    def __init__(self):
        self.supported_platforms = ['amazon', 'aliexpress', 'noon', 'all']
        
    def search_products(self, query, country, platform):
        """بحث ذكي في منصات متعددة"""
        logger.info(f"بحث عن: {query} في {platform} للسوق {country}")
        
        # بيانات تجريبية شاملة
        sample_products = self.generate_sample_data(query, country, platform)
        return sample_products
    
    def generate_sample_data(self, query, country, platform):
        """توليد بيانات منتجات تجريبية شاملة"""
        products = []
        
        for i in range(5):
            base_price = 100 if country == 'sa' else 500
            currency = 'ريال' if country == 'sa' else 'جنيه'
            
            product = {
                "id": f"{platform}-{i+1}",
                "name_ar": f"{query} الاحترافي #{i+1}",
                "name_en": f"Professional {query} #{i+1}",
                "image": f"https://picsum.photos/300/200?random={i}",
                "short_description": f"أفضل {query} في السوق بجودة ممتازة وتصميم عصري",
                "category": query,
                # ... باقي المحتوى كما في الكود الأصلي
            }
            products.append(product)
        
        return products

# تهيئة المحلل
analyzer = SmartProductAnalyzer()

@app.route('/')
def serve_frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.get_json() or {}
        query = data.get('query', '').strip()
        country = data.get('country', 'sa')
        platform = data.get('platform', 'all')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "يرجى إدخال مجال المنتجات للبحث"
            }), 400
        
        logger.info(f"طلب تحليل: {query} - {country} - {platform}")
        
        # البحث والتحليل
        products = analyzer.search_products(query, country, platform)
        
        return jsonify({
            "success": True,
            "query": query,
            "country": country,
            "platform": platform,
            "products_count": len(products),
            "products": products,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"خطأ في التحليل: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"حدث خطأ في النظام: {str(e)}"
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "running",
        "service": "Smart Product Analyzer",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/frontend/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/')
def home():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
