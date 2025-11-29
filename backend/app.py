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
        
        # بيانات تجريبية شاملة - يمكن استبدالها بـ APIs حقيقية
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
                "difficulty": "⭐" * (i % 3 + 1),
                "why_win": "طلب مرتفع وتكلفة منخفضة وهامش ربح عالي",
                "target": "شباب ومراهقين" if i % 2 == 0 else "عائلات ومحترفين",
                "age_range": "18-35" if i % 2 == 0 else "25-45",
                "gender": "ذكر" if i % 3 == 0 else "أنثى" if i % 3 == 1 else "كلا",
                "interests": ["تسوق", "موضة", "تقنية", "لياقة بدنية"],
                "problem": "يحل مشكلة الحاجة لمنتج عملي بجودة عالية وسعر معقول",
                
                "profit_analysis": {
                    "purchase_price": base_price + (i * 20),
                    "suggested_price": (base_price + (i * 20)) * 2,
                    "profit_margin": "45%",
                    "total_costs": (base_price + (i * 20)) * 0.3,
                    "net_profit": (base_price + (i * 20)) * 0.7,
                    "currency": currency
                },
                
                "suppliers": {
                    "local": [
                        {
                            "name": "مورد محلي #1",
                            "contact": "0551234567",
                            "link": "#"
                        }
                    ],
                    "international": [
                        {
                            "name": "AliExpress",
                            "link": "https://aliexpress.com",
                            "min_order": "1 قطعة"
                        }
                    ],
                    "shipping_days": "7-14 يوم",
                    "min_order": "1 قطعة"
                },
                
                "marketing": {
                    "platform": "تيك توك وإنستغرام",
                    "ad_copy": f"🔥 اكتشف أفضل {query} في السوق! 🔥\nجودة ممتازة ⭐ سعر لا يُنافس 🎯 توصيل سريع 🚚",
                    "video_idea": "عرض عملي للمنتج مع مقارنة الأسعار والجودة",
                    "hashtags": [f"#{query}", "#تسوق", "#عروض", "#جودة"],
                    "ad_budget": f"{50 + i * 10} {currency}/يوم"
                },
                
                "market_analysis": {
                    "competition": "منخفض" if i % 3 == 0 else "متوسط" if i % 3 == 1 else "عالي",
                    "demand": "مستمر" if i % 2 == 0 else "موسمي",
                    "unique_point": "جودة عالية وسعر تنافسي وتصميم مميز",
                    "growth_prediction": f"+{15 + i * 5}% خلال 2024"
                },
                
                "tips": [
                    "ركز على التسويق عبر منصات الفيديو القصيرة",
                    "التقط صور احترافية للمنتج من زوايا متعددة",
                    "قدم ضمان مجاني لأول 30 يوم",
                    "استخدم التوصيل السريع كعامل تمييز"
                ],
                
                "timestamp": datetime.now().isoformat(),
                "source": platform,
                "country": country
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

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
