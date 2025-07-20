from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import json
import os
from django.conf import settings
from sklearn.cluster import KMeans
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging

# Set up logging
logger = logging.getLogger(__name__)

def skin_analysis(request):
    """Render the skin analysis page"""
    return render(request, 'virtual_makeup/skin_analysis.html')

@csrf_exempt
def analyze_skin(request):
    """Process image and get skin analysis"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            skin_pixels = data.get('face_data', {}).get('skin_pixels', [])
            
            if not skin_pixels:
                logger.warning("No skin pixels detected in the request")
                return JsonResponse({'error': 'No skin pixels detected'}, status=400)
                
            # Analyze skin with enhanced algorithm
            skin_metrics = analyze_skin_from_pixels(skin_pixels)
            logger.info(f"Skin analysis completed: {skin_metrics}")
            
            # Get recommendations
            recommendations = get_recommendations(skin_metrics)
            
            return JsonResponse({
                'skin_analysis': skin_metrics,
                'recommendations': recommendations
            })
            
        except Exception as e:
            logger.error(f"Error in analyze_skin: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def analyze_skin_from_pixels(skin_pixels):
    """Enhanced skin analysis algorithm"""
    try:
        skin_pixels = np.array(skin_pixels)
        if len(skin_pixels) == 0:
            return default_skin_analysis()
            
        # Calculate average RGB and luminance
        avg_rgb = np.mean(skin_pixels, axis=0)
        r, g, b = avg_rgb
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        
        # Skin tone classification
        if luminance > 200:
            tone = '1'; desc = 'Very Fair'
        elif luminance > 180:
            tone = '2'; desc = 'Fair'
        elif luminance > 160:
            tone = '3'; desc = 'Light to Medium'
        elif luminance > 140:
            tone = '4'; desc = 'Medium to Tan'
        elif luminance > 120:
            tone = '5'; desc = 'Tan to Deep'
        else:
            tone = '6'; desc = 'Deep'
            
        # Skin type analysis
        rb_ratio = r / max(b, 1)
        if rb_ratio > 1.3 and np.std(skin_pixels[:, 0]) < 20:
            skin_type = 'dry'
        elif rb_ratio < 1.1 and b > 100:
            skin_type = 'oily'
        elif np.std(skin_pixels[:, 0]) > 25:
            skin_type = 'combination'
        else:
            skin_type = 'normal'
            
        # Acne detection
        red_pixels = len([p for p in skin_pixels if p[0] > 1.3*p[1] and p[0] > 1.3*p[2]])
        acne_percent = (red_pixels / len(skin_pixels)) * 100
        acne = 'High' if acne_percent > 8 else 'Moderate' if acne_percent > 4 else 'Low'
        
        return {
            'type': skin_type,
            'tone': tone,
            'tone_description': desc,
            'acne': acne,
            'metrics': {
                'luminance': round(float(luminance), 2),
                'red_blue_ratio': round(float(rb_ratio), 2),
                'acne_percent': round(float(acne_percent), 2)
            }
        }
        
    except Exception as e:
        print(f"Skin analysis error: {str(e)}")
        return default_skin_analysis()

def default_skin_analysis():
    return {
        'type': 'normal',
        'tone': '3',
        'tone_description': 'Medium',
        'acne': 'Low'
    }

def get_recommendations(skin_metrics):
    """Get product recommendations based on skin analysis"""
    skin_type = skin_metrics.get('type', 'normal')
    skin_tone = skin_metrics.get('tone', '3')
    acne_level = skin_metrics.get('acne', 'Low')
    
    # Enhanced product database with more specific skin concerns
    product_db = {
        'cleansers': [
            {
                'name': 'O3+ Anti Ageing Facial kit Brightening & Finelines Reducer With Peel off Mask ',
                'brand': 'O3+',
                'skin type': 'normal',
                'concern': ['daily cleansing'],
                'price': 532,
                'img': 'https://m.media-amazon.com/images/I/61L328jCs1L._SL1500_.jpg',
                'url': 'https://www.amazon.in/O3-Ageing-Brightening-Finelines-Reducer/dp/B09MHCJ8SC/ref=sr_1_2_sspa?crid=10OSBWCTDZ54H&dib=eyJ2IjoiMSJ9.Ry0YKLVPE1MuoPdh3eE_m4X7ay1MhqMyYQmyfP5eA8Z2kZPR1d4dms04gIcV0DOhbs3B3UtAOXvesavZ5WxI8tCwznFRB_7tn0C-4PbhjlHkFd6-xzb46AKk_Unzo_Te6WLcCINSdG3YwQnw74h3PiOQlsSq-8gk9QqNW8wLbAyjh7xeSvzJGkHm9d8uX7f2rQYyX6GPb9q26baO7SttkuPpEAVt0gl3EM6mxDGFFFqQnjHPm8FH5zRCuXMbgWydT8bS3DgsIAfHClp8zPny1wFJ5k-B2phf01-pHd2GMhI.YfcH3MX22qZPq8FW0KSrMg-Ffsd0O1megeZwqyGWZMY&dib_tag=se&keywords=skin%2Bcare%2Boil%2Bproducts&qid=1744150279&sprefix=skin%2Bcare%2Boili%2Bproducts%2Caps%2C285&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1'
            },
            {
                'name': 'Neutrogena Hydro Boost Water Gel Cleanser',
                'brand': 'Neutrogena',
                'skin type': 'dry',
                'concern': ['hydration'],
                'price': 9.99,
                'img': 'https://m.media-amazon.com/images/I/51DyW1rvfuL._SL1000_.jpg',
                'url': 'https://www.amazon.in/Neutrogena-Hydro-Boost-Cleanser-Transparent/dp/B077NXTT3Q?th=1'
            },
            {
                'name': 'Clean & Clear Foaming Face Wash For Oily Skin',
                'brand': 'Clean & Clear',
                'skin type': 'oily',
                'concern': ['oil control'],
                'price': 235,
                'img': 'https://m.media-amazon.com/images/I/51+8qn67b0L._SL1080_.jpg',
                'url': 'https://www.amazon.in/Clean-Clear-Foaming-Face-Wash/dp/B00CI3HDMU?utm_source=chatgpt.com&th=1'
            },
            {
                'name': 'Effaclar Medicated Cleanser',
                'brand': 'La Roche-Posay',
                'skin type': 'combination',
                'concern': ['acne', 'balance'],
                'price': 111,
                'img': 'https://m.media-amazon.com/images/I/61eeFlpzxRL._AC_SL1500_.jpg',
                'url': 'https://www.amazon.ae/Roche-Posay-Effaclar-Medicated-Cleanser-Salicylic/dp/B00LO1DNXU?utm_source=chatgpt.com'
            },
            {
                'name': 'Sensitive Skin Cleanser',
                'brand': 'Cetaphil',
                'skin type': 'dry',
                'concern': ['sensitive skin', 'gentle'],
                'price': 377,
                'img': 'https://m.media-amazon.com/images/I/51O+J5jnXcL._SL1000_.jpg',
                'url': 'https://www.amazon.in/Cetaphil-Gentle-Skin-Cleanser-125ml/dp/B01CCGW4OE?utm_source=chatgpt.com&th=1'
            },
            {
                'name': 'Acne Foaming Cream Cleanser',
                'brand': 'Clearasil',
                'skin type': 'oily',
                'concern': ['acne', 'deep cleaning'],
                'price': 1201,
                'img': 'https://images.meesho.com/images/products/454371790/d720n_512.webp',
                'url': 'https://www.meesho.com/cerave-acne-foaming-cream-wash-150ml/p/7iirim'
            }
        ],
        'moisturizers': [
            {
                'name': 'CeraVe Daily Moisturizing Lotion',
                'brand': 'CeraVe',
                'skin type': 'normal',
                'concern': ['hydration'],
                'price': 13,
                'img': 'https://m.media-amazon.com/images/I/61jeXEEvGAL._SL1500_.jpg',
                'url': 'https://www.amazon.com/CeraVe-Moisturizing-Lotion-Hyaluronic-Fragrance/dp/B000YJ2SLG?utm_source=chatgpt.com&th=1'
            },
            {
                'name': 'Neutrogena Hydro Boost Hyaluronic Acid Face Moisturizer',
                'brand': 'Neutrogena',
                'skin type': 'dry',
                'concern': ['hydration', 'lightweight'],
                'price': 394,
                'img': 'https://m.media-amazon.com/images/G/31/apparel/rcxgs/tile._CB483369979_.gif',
                'url': 'https://www.amazon.in/Neutrogena-Hydro-Boost-Water-White/dp/B08HRCNFCM?utm_source=chatgpt.com&th=1'
            },
            {
                'name': 'Intense Hydration Cream Moisture',
                'brand': 'Neutrogena',
                'skin type': 'dry',
                'concern': ['intense hydration'],
                'price': 770,
                'img': 'https://m.media-amazon.com/images/I/510eWZCb3IL._SL1000_.jpg',
                'url': 'https://www.amazon.in/Neutrogena-Oil-Free-Moisture-SPF-115ML/dp/B0B18MRNG1/ref=sr_1_9?dib=eyJ2IjoiMSJ9.Red9VNCWE8KOMjQoNpwaHKKyheFTHXKWcn3VhfXpteTV_wbb7o8PHx6A-_tQ26vZxmMKCdNGdtG1ZXhfF01wDb1bEIVl312Bdrvr4m2uz9OVuQXMHZwTAcIkZL7JMIdjU2kP6rZscAvBoe4goKkyluGz5NYALdxbCEZ3HdKKjqYTq6_l0m4O22w1L90iyDIJXsxugucPkOwZ8q82IlUn9yVJBL-CnITNd6AKg0n-2WiTf0yJcraZycHdnU6fv7pnJFZ7cGXWm14O7BQifdQYl0jvgav8XwAhpLGhx6S5hE8.-Mgx8NAo_D5LBzrHyA6q8qu3e6GD28IN878iai8PNE4&dib_tag=se&qid=1744369593&refinements=p_89%3ANeutrogena&s=beauty&sr=1-9&utm_source=chatgpt.com'
            },
            {
                'name': 'Oil-Free Moisturizer',
                'brand': 'Clean & Clear',
                'skin type': 'oily',
                'concern': ['oil control', 'hydration'],
                'price': 140,
                'img': 'https://smytten-image.gumlet.io/shop_item/CAC0005AB1O1.jpg',
                'url': 'https://smytten.com/shop/product/cleansers/pimple-clearing-face-wash/CAC0005AB1'
            },
            {
                'name': 'Balancing Moisturizer',
                'brand': 'La Roche-Posay',
                'skin type': 'combination',
                'concern': ['balance', 'hydration'],
                'price': 34.10,
                'img': 'https://cdn.cosmostore.org/cache/front/shop/products/513/1563990/350x350.jpg',
                'url': 'https://cosmostore.in/catalog/product/effaclar_mat_daily_moisturizer_new_formula_for_oily_skin_40ml_135oz/?utm_source=chatgpt.com'
            },
            {
                'name': 'Ultra Repair Cream Intense Hydration',
                'brand': 'First Aid Beauty',
                'skin type': 'normal',
                'concern': ['intense repair', 'sensitive'],
                'price': 38,
                'img': 'https://www.firstaidbeauty.com/cdn/shop/files/UltraRepairCream_6oz_Lead_2000x2000_d8b2f943-720b-438d-bf22-b3a8cd497298.jpg?v=1716235447&width=823',
                'url': 'https://www.firstaidbeauty.com/products/ultra-repair-cream-intense-hydration?bvstate=pg%3A79%2Fct%3Ar&srsltid=AfmBOoq9PLcNYJSE434t4yXDnYyjMGQtr7fXAku86alPS4G5WGjehrfs&utm_source=chatgpt.com'
            }
        ],
        'serums': [
            {
                'name': 'The Ordinary Vitamin C Vitamin C Serum',
                'brand': 'The Ordinary',
                'skin type': 'all',
                'concern': ['brightening', 'antioxidant'],
                'price': 900,
                'img': 'https://images-static.nykaa.com/media/catalog/product/2/1/21daf06769915196061_1.jpg',
                'url': 'https://www.nykaa.com/the-ordinary-vitamin-c-suspension-23percent-ha-spheres-2percent/p/5003167'
            },
            {
                'name': 'THE ORDINARY Deciem Hyaluronic Acid',
                'brand': 'The Ordinary',
                'skin type': 'dry',
                'concern': ['hydration', 'plumping'],
                'price': 6.99,
                'img': 'https://m.media-amazon.com/images/I/41QX2rGH4XL._SL1500_.jpg',
                'url': 'https://www.amazon.in/Deciem-Ordinary_Hyaluronic-_Free-Standard-Shipping/dp/B07DBM5J2D?utm_source=chatgpt.com'
            },
            {
                'name': 'Niacinamide Serum 10% + Zinc 1%',
                'brand': 'The Ordinary',
                'skin type': 'oily',
                'concern': ['oil control', 'pores'],
                'price': 5.99,
                'img': 'https://theordinary.com/dw/image/v2/BFKJ_PRD/on/demandware.static/-/Sites-deciem-master/default/dwce8a7cdf/Images/products/The%20Ordinary/rdn-niacinamide-10pct-zinc-1pct-30ml.png?sw=800&sh=800&sm=fit',
                'url': 'https://theordinary.com/en-in/niacinamide-10-zinc-1-serum-100436.html?utm_source=chatgpt.com'
            },
            {
                'name': 'The Derma Co 2% Salicylic Acid Face Serum',
                'brand': 'The Ordinary',
                'skin type': 'combination',
                'concern': ['acne', 'exfoliation'],
                'price': 424,
                'img': 'https://m.media-amazon.com/images/I/510XARlsJ1L._SL1200_.jpg',
                'url': 'https://www.amazon.in/Derma-Co-Salicylic-Serum-Marks/dp/B08TT6DPXN/ref=dp_fod_d_sccl_1/257-3034429-9902920?pd_rd_w=IwjDe&content-id=amzn1.sym.2c0bc63e-7045-4193-97df-fbe90f6fe0c3&pf_rd_p=2c0bc63e-7045-4193-97df-fbe90f6fe0c3&pf_rd_r=SQFJK1BQSVP01AC6MMVV&pd_rd_wg=Xes27&pd_rd_r=fedd4132-226f-4fe5-894b-b010d019ea8d&pd_rd_i=B08TT6DPXN&th=1'
            },
            {
                'name': 'INKEY List Collagen Peptide Serum ',
                'brand': 'The Inkey List',
                'skin type': 'oily',
                'concern': ['anti-aging', 'texture'],
                'price': 5355,
                'img': 'https://images-cdn.ubuy.co.in/6442e03e3bf97125ea61be54-the-inkey-list-collagen-peptide-serum.jpg',
                'url': 'https://www.ubuy.co.in/product/2F0CGTM-inkey-list-collagen-booster'
            },
            {
                'name': 'PAULAS CHOICE SKIN PERFECTING',
                'brand': 'Paulas Choice',
                'skin type': 'combination',
                'concern': ['acne', 'redness', 'texture'],
                'price': 1200,
                'img': 'https://m.media-amazon.com/images/I/61+zhXW9-+L._SL1500_.jpg',
                'url': 'https://www.amazon.in/Choice-SKIN-PERFECTING-Exfoliant-Facial-Blackheads-Lines-1-1oz/dp/B07C5SS6YD/ref=pd_bxgy_thbs_d_sccl_1/257-3034429-9902920?pd_rd_w=r8qCW&content-id=amzn1.sym.e933bed8-66b5-4e19-9aeb-b2834144fba3&pf_rd_p=e933bed8-66b5-4e19-9aeb-b2834144fba3&pf_rd_r=1JHBX0B174RRX9WJ62HP&pd_rd_wg=gCmDl&pd_rd_r=b11a918b-4da4-4c1c-b064-2b60ed6a09a8&pd_rd_i=B07C5SS6YD&th=1'
            }
        ],
        'makeup': [
            # Very Fair (1)
            {
                'name': 'FIT ME MATTE + PORELESS LIQUID FOUNDATION ',
                'brand': 'Maybelline',
                'skin type': 'oily',
                'concern': ['coverage'],
                'tone': '1',
                'price': 649,
                'img': 'https://www.maybelline.co.in/-/media/project/loreal/brand-sites/mny/apac/in/products/face/foundation/fitme-matte-and-poreless-foundation/modules/product-info/230-natural-buff/fmt-bottle_230.jpg?rev=881764efe2e84c01bee18f961dec3ec6&cx=0&cy=0&cw=315&ch=472&hash=953BA0BC0E8C536ECEDE2FD7981C4FB3',
                'url': 'https://www.maybelline.co.in/all-products/face/foundation/fit-me-foundation?variant=Natural-Buff'
            },
            {
                'name': 'Maybelline New York Fit Me Concealer',
                'brand': 'Maybelline',
                'skin type': 'normal',
                'concern': ['coverage', 'blemish'],
                'tone': '1',
                'price': 494,
                'img': 'https://m.media-amazon.com/images/G/31/apparel/rcxgs/tile._CB483369979_.gif',
                'url': 'https://www.amazon.in/Maybelline-Concealer-Poreless-Liquid-Foundation/dp/B08PD91LCP?utm_source=chatgpt.com'
            },
            # Fair (2)
            {
                'name': 'Fit Me Foundation - Fair Ivory',
                'brand': 'Maybelline',
                'skin type': 'normal',
                'concern': ['coverage'],
                'tone': '2',
                'price': 675,
                'img': 'https://m.media-amazon.com/images/I/51rcd4pMYvL._SL1250_.jpg',
                'url': 'https://www.amazon.in/dp/B007MJKI22/ref=sspa_dk_detail_0?psc=1&pd_rd_i=B007MJKI22&pd_rd_w=RBqJK&content-id=amzn1.sym.9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_p=9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_r=FMJ74P4CJR6HPY89QJE6&pd_rd_wg=9dBNt&pd_rd_r=13e0e9ad-84f0-4e51-9153-2345677bee2f&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM'
            },
            {
                'name': 'Estee Lauder Double Wear Stay-In-Place Makeup Foundation',
                'brand': 'Estée Lauder',
                'skin type': 'combination',
                'concern': ['coverage', 'long-lasting'],
                'tone': '2',
                'price': 4300,
                'img': 'https://cdn.tirabeauty.com/v2/billowing-snowflake-434234/tira-p/wrkr/products/pictures/item/free/original/1021637/RJ6Qp-XaDJ-1021637_1.jpg?dpr=1',
                'url': 'https://www.tirabeauty.com/product/estee-lauder-double-wear-stay-in-place-makeup-foundation-spf-10---1n2-ecru-30ml-0s0fue13hjom'
            },
            # Light to Medium (3)
            {
                'name': 'Maybelline Fit Me Foundation SPF 18',
                'brand': 'Maybelline',
                'skin type': 'normal',
                'concern': ['coverage'],
                'tone': '3',
                'price': 1770,
                'img': 'https://www.topprice.in/image/cache/catalog/datayuge_feed/e9b1f0ff16e273651511e5dea7c969602fa603df-600x600.jpg',
                'url': 'https://www.topprice.in/maybelline-fit-me-foundation-spf-18-classic-ivory-120-p141849?utm_source=chatgpt.com'
            },
            {
                'name': 'LOréal Paris True Match Super-Blendable Compact ',
                'brand': 'L\'Oréal',
                'skin type': 'normal',
                'concern': ['natural finish'],
                'tone': '3',
                'price': 8167,
                'img': 'https://m.media-amazon.com/images/I/51Zd82vmLmL._SX300_SY300_QL70_ML2_.jpg',
                'url': 'https://www.amazon.in/LOr%C3%A9al-Paris-Super-Blendable-Compact-Makeup/dp/B002LKCI2U?utm_source=chatgpt.com&th=1'
            },
            # Medium to Tan (4)
            {
                'name': 'RDE home care BB Glow Treatment Kit Medium Coverage Foundation ',
                'brand': 'Maybelline',
                'skin type': 'normal',
                'concern': ['coverage'],
                'tone': '4',
                'price': 1799,
                'img': 'https://m.media-amazon.com/images/I/61tq4zrBe6L.jpg',
                'url': 'https://www.amazon.in/dp/B0D4DQC9L8/ref=sspa_dk_detail_6?psc=1&pd_rd_i=B0D4DQC9L8&pd_rd_w=C6qwI&content-id=amzn1.sym.9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_p=9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_r=CQX1NYBZ54QVHJDBJX0B&pd_rd_wg=CCeLv&pd_rd_r=70f0a725-d0e5-4595-97bf-bcbc03b09df9&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM'
            },
            {
                'name': 'Double Wear Stay-In-Place Makeup SPF 10',
                'brand': 'Estée Lauder',
                'skin type': 'combination',
                'concern': ['coverage', 'long-lasting'],
                'tone': '4',
                'price': 4500,
                'img': 'https://cdn.fynd.com/v2/falling-surf-7c8bb8/fyprod/wrkr/products/pictures/item/free/resize-w:1024/000000000491942304/ABaQVO6Mpw-000000000491942304_1.png',
                'url': 'https://sephora.in/product/estee-lauder-double-wear-stay-in-place-makeup-spf-10-foundation-v-3w1-tawny-medium-with-warm-golden-undertones?utm_source=chatgpt.com'
            },
            # Tan to Deep (5)
            {
                'name': 'Bio-Oil Original Skincare Oil suitable for Stretch Marks | Scar Removal | Uneven Skin Tone | Vitamin E | All Skin Types ',
                'brand': 'Bio-Oil',
                'skin type': 'combination',
                'concern': ['coverage'],
                'tone': '5',
                'price': 437,
                'img': 'https://m.media-amazon.com/images/I/71yl5mKbEnL._SL1500_.jpg',
                'url': 'https://www.amazon.in/Bio-Oil-Specialist-Skincare-Oil-60ml/dp/B00GMC04BK/ref=sr_1_5?crid=10OSBWCTDZ54H&dib=eyJ2IjoiMSJ9.Ry0YKLVPE1MuoPdh3eE_m4X7ay1MhqMyYQmyfP5eA8Z2kZPR1d4dms04gIcV0DOhbs3B3UtAOXvesavZ5WxI8tCwznFRB_7tn0C-4PbhjlHkFd6-xzb46AKk_Unzo_Te6WLcCINSdG3YwQnw74h3PiOQlsSq-8gk9QqNW8wLbAyjh7xeSvzJGkHm9d8uX7f2rQYyX6GPb9q26baO7SttkuPpEAVt0gl3EM6mxDGFFFqQnjHPm8FH5zRCuXMbgWydT8bS3DgsIAfHClp8zPny1wFJ5k-B2phf01-pHd2GMhI.YfcH3MX22qZPq8FW0KSrMg-Ffsd0O1megeZwqyGWZMY&dib_tag=se&keywords=skin+care+oil+products&qid=1744150279&sprefix=skin+care+oili+products%2Caps%2C285&sr=8-5'
            },
            {
                'name': 'Orimii Bump Hydrating Stretch Marks Body Butter',
                'brand': 'ORIMII',
                'skin type': 'normal',
                'concern': ['natural finish'],
                'tone': '5',
                'price': 660,
                'img': 'https://m.media-amazon.com/images/I/41ZY9kHlPeL._SL1500_.jpg',
                'url': 'https://www.amazon.in/dp/B0B4JWHFD2/ref=sspa_dk_detail_3?psc=1&pd_rd_i=B0B4JWHFD2&pd_rd_w=yGWmU&content-id=amzn1.sym.9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_p=9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_r=G0XEZVGB5X1BZAADCYP2&pd_rd_wg=5Bk8v&pd_rd_r=96a2372c-b12f-4718-8a1e-0a1504aedbc1&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM'
            },
            # Deep (6)
            {
                'name': 'Luciara® Cream, Anti-stretch marks cream, Reduce stretchmarks',
                'brand': 'Luciara',
                'skin type': 'oily',
                'concern': ['coverage'],
                'tone': '6',
                'price': 369,
                'img': 'https://m.media-amazon.com/images/I/61367n3Y5EL._SL1500_.jpg',
                'url': 'https://www.amazon.in/dp/B09B9G6KQB/ref=sspa_dk_detail_6?pd_rd_i=B09B9G6KQB&pd_rd_w=yGWmU&content-id=amzn1.sym.9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_p=9f1cb690-f0b7-44de-b6ff-1bad1e37d3f0&pf_rd_r=G0XEZVGB5X1BZAADCYP2&pd_rd_wg=5Bk8v&pd_rd_r=96a2372c-b12f-4718-8a1e-0a1504aedbc1&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM&th=1'
            },
            {
                'name': 'EQUALSTWO Anti Stretch Mark Oil, 200ml',
                'brand': 'Estée Lauder',
                'skin type': 'combination',
                'concern': ['coverage', 'long-lasting'],
                'tone': '6',
                'price': 1273,
                'img': 'https://m.media-amazon.com/images/I/81O3xipBQ5L._SL1500_.jpg',
                'url': 'https://www.amazon.in/dp/B0C6K1Y632/ref=sspa_dk_detail_2?pd_rd_i=B0C6K1Y632&pd_rd_w=pXVzj&content-id=amzn1.sym.b4e5ca1f-7c9f-49a0-abff-111b926d76ce&pf_rd_p=b4e5ca1f-7c9f-49a0-abff-111b926d76ce&pf_rd_r=5JBB6AFA616ZHXW29SF9&pd_rd_wg=mhRFv&pd_rd_r=2645c15b-efee-4c5c-9b1d-ede61b1154fd&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM&th=1'
            }
        ]
    }
    
    # Filter products based on skin metrics with more sophisticated logic
    
    # 1. Filter cleansers based on skin type and acne concerns
    filtered_cleansers = []
    
    # If acne is a concern, prioritize acne-fighting cleansers
    if acne_level == 'Moderate' or acne_level == 'High':
        filtered_cleansers = [p for p in product_db['cleansers'] 
                             if 'acne' in str(p['concern']).lower() and
                             (p['skin type'] == skin_type or p['skin type'] == 'all')]
        
        # Add non-acne cleansers for the skin type as backup
        if len(filtered_cleansers) < 2:
            filtered_cleansers += [p for p in product_db['cleansers'] 
                                 if 'acne' not in str(p['concern']).lower() and
                                 (p['skin type'] == skin_type or p['skin type'] == 'all')]
    else:
        # For low acne, focus on skin type
        filtered_cleansers = [p for p in product_db['cleansers'] 
                             if p['skin type'] == skin_type or p['skin type'] == 'all']
    
    # 2. Filter moisturizers with similar logic
    filtered_moisturizers = []
    
    # For dry skin or winter, prioritize intense hydration
    if skin_type == 'dry':
        filtered_moisturizers = [p for p in product_db['moisturizers'] 
                               if 'intense' in str(p['concern']).lower() and
                               (p['skin type'] == skin_type or p['skin type'] == 'all')]
    elif skin_type == 'oily':
        # For oily skin, prioritize oil control moisturizers
        filtered_moisturizers = [p for p in product_db['moisturizers'] 
                               if 'oil control' in str(p['concern']).lower() and
                               (p['skin type'] == skin_type or p['skin type'] == 'all')]
    else:
        # For normal/combination, use skin type as primary filter
        filtered_moisturizers = [p for p in product_db['moisturizers'] 
                               if p['skin type'] == skin_type or p['skin type'] == 'all']
    
    # 3. Filter serums based on skin concerns
    filtered_serums = []
    
    # Acne treatment takes priority for moderate to high acne
    if acne_level == 'Moderate' or acne_level == 'High':
        filtered_serums = [p for p in product_db['serums'] 
                          if 'acne' in str(p['concern']).lower()]
        
        # Add products for skin type
        filtered_serums += [p for p in product_db['serums'] 
                           if p['skin type'] == skin_type or p['skin type'] == 'all']
    elif skin_type == 'dry':
        # For dry skin, prioritize hydration
        filtered_serums = [p for p in product_db['serums'] 
                          if 'hydration' in str(p['concern']).lower() or
                             'plumping' in str(p['concern']).lower()]
    elif skin_type == 'oily':
        # For oily skin, prioritize oil control and pore concerns
        filtered_serums = [p for p in product_db['serums'] 
                          if 'oil control' in str(p['concern']).lower() or
                             'pore' in str(p['concern']).lower()]
    else:
        # For normal/combination skin
        filtered_serums = [p for p in product_db['serums']]
    
    # 4. Filter makeup based primarily on skin tone
    filtered_makeup = [p for p in product_db['makeup'] if p.get('tone') == skin_tone]
    
    # If no exact match, use products for all skin tones or nearest match
    if not filtered_makeup:
        tone_int = int(skin_tone)
        # Find products with closest tone
        filtered_makeup = [p for p in product_db['makeup'] 
                         if abs(int(p.get('tone', '3')) - tone_int) <= 1]
    
    # Package recommendations with uniqueness
    filtered_cleansers = list({p['name']: p for p in filtered_cleansers}.values())
    filtered_moisturizers = list({p['name']: p for p in filtered_moisturizers}.values())
    filtered_serums = list({p['name']: p for p in filtered_serums}.values())
    filtered_makeup = list({p['name']: p for p in filtered_makeup}.values())
    
    recommendations = {
        'makeup': filtered_makeup[:3],  # Limit to 3 items
        'general': {
            'cleanser': filtered_cleansers[:3],
            'moisturizer': filtered_moisturizers[:3],
            'serum': filtered_serums[:3]
        }
    }
    
    return recommendations


def send_recommendations_email(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        email = request.POST.get('email')
        skin_type = request.POST.get('skin_type')
        skin_tone = request.POST.get('skin_tone')
        acne_level = request.POST.get('acne_level')
        
        try:
            recommendations = json.loads(request.POST.get('recommendations_json', '{}'))
            
            # Create context for email template
            context = {
                'skin_type': skin_type,
                'skin_tone': skin_tone,
                'acne_level': acne_level,
                'makeup_recommendations': recommendations.get('makeup', []),
                'cleanser_recommendations': recommendations.get('general', {}).get('cleanser', []),
                'moisturizer_recommendations': recommendations.get('general', {}).get('moisturizer', []),
                'serum_recommendations': recommendations.get('general', {}).get('serum', []),
            }
            
            # Render email content
            email_html = render_to_string('email_recommendations.html', context)
            email_plain = render_to_string('email_recommendations_plain.html', context)
            
            # Send email
            send_mail(
                subject='Your Beauty Product Recommendations',
                message=email_plain,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=email_html,
                fail_silently=False,
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})