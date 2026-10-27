import random
from app.database import get_db_connection

# Curated Unsplash HD photos categorized for realistic display
CATEGORY_IMAGES = {
    "Dairy, Bread & Eggs": [
        "https://images.unsplash.com/photo-1528750997573-59b89d56f4f7?auto=format&fit=crop&w=400&q=80", # Milk
        "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&w=400&q=80", # Cheese
        "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=400&q=80", # Bread
        "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=400&q=80", # Eggs
        "https://images.unsplash.com/photo-1486297678162-eb2a19b0a32d?auto=format&fit=crop&w=400&q=80", # Butter
        "https://images.unsplash.com/photo-1571212515416-fef01fc43637?auto=format&fit=crop&w=400&q=80", # Yogurt
    ],
    "Fresh Fruits & Vegetables": [
        "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=400&q=80", # Fresh fruit
        "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=400&q=80", # Veggies
        "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=400&q=80", # Apples
        "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=400&q=80", # Bananas
        "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=400&q=80", # Potatoes
        "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=400&q=80", # Tomatoes
        "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=400&q=80", # Spinach
    ],
    "Snacks & Munchies": [
        "https://images.unsplash.com/photo-1566478989037-eec170784d0b?auto=format&fit=crop&w=400&q=80", # Chips
        "https://images.unsplash.com/photo-1621996346565-e3d5d6281691?auto=format&fit=crop&w=400&q=80", # Snacks
        "https://images.unsplash.com/photo-1587132137056-bfbf0166836e?auto=format&fit=crop&w=400&q=80", # Popcorn
        "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&w=400&q=80", # Nachos
        "https://images.unsplash.com/photo-1508737804141-4c3b688e2546?auto=format&fit=crop&w=400&q=80", # Nuts
    ],
    "Instant & Frozen Food": [
        "https://images.unsplash.com/photo-1612927601601-6638404737ce?auto=format&fit=crop&w=400&q=80", # Noodles
        "https://images.unsplash.com/photo-1569058242253-92a9c755a0ec?auto=format&fit=crop&w=400&q=80", # Fries
        "https://images.unsplash.com/photo-1534422298391-e4f8c172dddb?auto=format&fit=crop&w=400&q=80", # Momos/Dumplings
        "https://images.unsplash.com/photo-1547592166-23ac45744acd?auto=format&fit=crop&w=400&q=80", # Soup
    ],
    "Cold Drinks & Juices": [
        "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?auto=format&fit=crop&w=400&q=80", # Soda can
        "https://images.unsplash.com/photo-1600271886742-f049cd451bba?auto=format&fit=crop&w=400&q=80", # Orange juice
        "https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=400&q=80", # Drink
        "https://images.unsplash.com/photo-1527661591475-527312dd65f5?auto=format&fit=crop&w=400&q=80", # Energy drink
    ],
    "Bakery & Biscuits": [
        "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?auto=format&fit=crop&w=400&q=80", # Cookies
        "https://images.unsplash.com/photo-1579372786545-d24232daf58c?auto=format&fit=crop&w=400&q=80", # Cake
        "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=400&q=80", # Croissant
        "https://images.unsplash.com/photo-1586985289688-ca3cf47d3e6e?auto=format&fit=crop&w=400&q=80", # Pastry
    ],
    "Tea, Coffee & Beverages": [
        "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=400&q=80", # Tea
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=400&q=80", # Coffee
        "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=400&q=80", # Green Tea
    ],
    "Atta, Rice & Dals": [
        "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=400&q=80", # Rice
        "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&w=400&q=80", # Grains / Flour
        "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?auto=format&fit=crop&w=400&q=80", # Pulses
    ],
    "Masalas & Dry Fruits": [
        "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=400&q=80", # Spices
        "https://images.unsplash.com/photo-1508061253366-f7da158b6d46?auto=format&fit=crop&w=400&q=80", # Almonds/Dry fruits
        "https://images.unsplash.com/photo-1532336414038-cf19250c5757?auto=format&fit=crop&w=400&q=80", # Cashews
    ],
    "Cleaning & Household": [
        "https://images.unsplash.com/photo-1585421514738-01798e348b17?auto=format&fit=crop&w=400&q=80", # Detergent
        "https://images.unsplash.com/photo-1584813470613-5b1c1cad3d69?auto=format&fit=crop&w=400&q=80", # Cleaning spray
        "https://images.unsplash.com/photo-1563453392212-326f5e854473?auto=format&fit=crop&w=400&q=80", # Dishwash
    ],
    "Personal Care": [
        "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=400&q=80", # Skincare / Soap
        "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=400&q=80", # Shampoo
        "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=400&q=80", # Lotion
    ],
    "Baby Care": [
        "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=400&q=80", # Baby toy
        "https://images.unsplash.com/photo-1544126592-807ade215a0b?auto=format&fit=crop&w=400&q=80", # Baby care
    ],
    "Pet Supplies": [
        "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?auto=format&fit=crop&w=400&q=80", # Dog
        "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=400&q=80", # Cat
    ],
    "Pharma & Wellness": [
        "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=400&q=80", # Pills / Medicine
        "https://images.unsplash.com/photo-1587854692152-cbe660dbde88?auto=format&fit=crop&w=400&q=80", # Supplements
    ]
}

# Catalog Blueprint definition with items, brands, subcategories, units, and price baseline
CATALOG_BLUEPRINT = [
    {
        "category": "Fresh Fruits & Vegetables",
        "subcategories": ["Fresh Vegetables", "Fresh Fruits", "Exotic & Organic", "Herbs & Seasoning"],
        "items": [
            ("Farm Fresh Onion", "FreshFarm", 28, 40, "1 kg", "Pungent, crispy farm-picked onions."),
            ("Hybrid Red Tomatoes", "NatureFresh", 32, 45, "1 kg", "Firm, juicy and ripe red salad tomatoes."),
            ("Desi Potato / Aloo", "KisanChoice", 35, 48, "1 kg", "Fresh new-crop earthy potatoes."),
            ("Fresh Green Spinach (Palak)", "GreenLeaf", 25, 35, "250 g", "Tender leaves, washed and pesticide-free."),
            ("Coriander Leaves (Dhaniya)", "FreshFarm", 15, 22, "100 g", "Aromatic fresh green coriander bunch."),
            ("Green Chilli (Hari Mirch)", "FreshFarm", 18, 25, "100 g", "Spicy green chillies for daily cooking."),
            ("Shimla Capsicum Green", "NatureFresh", 38, 55, "500 g", "Crispy and vibrant bell peppers."),
            ("Crisp Cucumber (Kheera)", "NatureFresh", 29, 40, "500 g", "Hydrating fresh summer cucumbers."),
            ("Lady Finger (Bhindi)", "KisanChoice", 36, 50, "500 g", "Fresh tender okra, easy to cook."),
            ("Cauliflower (Phool Gobhi)", "GreenLeaf", 38, 52, "1 pc (approx 500g)", "White, firm and fresh cauliflower florets."),
            ("Cabbage (Patta Gobhi)", "GreenLeaf", 28, 40, "1 pc (approx 600g)", "Crunchy cabbage for salads and stir fry."),
            ("Fresh Ginger (Adrak)", "FreshFarm", 24, 35, "100 g", "Spicy aromatic culinary ginger root."),
            ("Garlic (Lehsun)", "FreshFarm", 45, 65, "200 g", "Peeled or fresh pods with strong aroma."),
            ("Button Mushrooms", "MushroomHub", 49, 65, "200 g pack", "Clean white farm button mushrooms."),
            ("Desi Carrot (Gajar)", "NatureFresh", 35, 50, "500 g", "Sweet and crunchy farm-picked carrots."),
            ("Lemon (Nimbu)", "FreshFarm", 20, 30, "4 pcs", "Juicy, thin-skinned yellow lemons."),
            ("Shimla Royal Apple", "KinnaurFresh", 120, 160, "4 pcs (approx 600g)", "Sweet, crisp red apples directly from Himachal."),
            ("Robusta Banana", "KisanChoice", 42, 55, "1 bunch (6 pcs)", "Naturally ripened potassium-rich bananas."),
            ("Pomegranate (Anaar)", "FruitKing", 145, 190, "3 pcs (approx 600g)", "Ruby red sweet arils rich in antioxidants."),
            ("Nagpur Orange (Santra)", "CitrusGrove", 75, 105, "1 kg", "Sweet and tangy juicy table oranges."),
            ("Sweet Papaya", "TropicalFresh", 55, 75, "1 pc (approx 800g)", "Ripened golden-orange sweet papaya."),
            ("Fresh Tender Coconut", "CocoExpress", 58, 75, "1 pc", "Sweet natural electrolyte water."),
            ("Green Kiwi Fruit", "Zespri", 99, 135, "3 pcs pack", "Tangy-sweet nutrient dense kiwis."),
            ("Hass Avocado", "GlobalFresh", 135, 180, "1 pc", "Creamy, buttery ready-to-eat ripe avocado."),
            ("Blueberries Imported", "BerryDelight", 189, 250, "125 g box", "Antioxidant-packed sweet plump berries."),
            ("Green Mint (Pudina)", "GreenLeaf", 12, 18, "100 g", "Cooling aromatic fresh mint leaves.")
        ]
    },
    {
        "category": "Dairy, Bread & Eggs",
        "subcategories": ["Milk & Cream", "Curd & Yogurt", "Butter & Cheese", "Bread & Pav", "Eggs"],
        "items": [
            ("Amul Taaza Homogenised Toned Milk", "Amul", 27, 28, "500 ml pouch", "Pasteurized toned fresh milk."),
            ("Amul Gold Full Cream Fresh Milk", "Amul", 33, 34, "500 ml pouch", "Rich creamy milk, ideal for tea and sweets."),
            ("Mother Dairy Cow Milk", "Mother Dairy", 28, 29, "500 ml", "Light, easily digestible farm cow milk."),
            ("Nandini GoodLife UHT Milk", "Nandini", 65, 68, "1 L tetra", "Long shelf life fresh toned milk."),
            ("Amul Salted Butter", "Amul", 56, 58, "100 g", "Utterly butterly delicious creamy yellow butter."),
            ("Amul Pasteurised Butter", "Amul", 265, 275, "500 g brick", "Classic Indian table butter."),
            ("Amul Malai Fresh Paneer", "Amul", 89, 95, "200 g pack", "Soft, succulent cottage cheese cubes."),
            ("Mother Dairy Classic Dahi", "Mother Dairy", 35, 38, "400 g cup", "Thick, creamy traditional set curd."),
            ("Epigamia Greek Yogurt Natural", "Epigamia", 55, 60, "90 g", "High protein probiotic smooth greek yogurt."),
            ("Britannia Cheese Slices", "Britannia", 125, 140, "10 slices (200g)", "Cheddar melt-in-mouth sandwich slices."),
            ("Amul Processed Cheese Block", "Amul", 130, 145, "200 g", "Rich cheesy block perfect for pizza & paratha."),
            ("Farm Fresh White Eggs", "Eggoz", 72, 85, "6 pcs tray", "UV sanitized, antibiotic-free farm eggs."),
            ("Brown Organic Free-Range Eggs", "Eggoz", 110, 135, "6 pcs tray", "Omega-3 rich pasture raised brown eggs."),
            ("English Oven 100% Whole Wheat Bread", "English Oven", 45, 50, "400 g", "Soft, fiber-rich brown sandwich bread."),
            ("Modern White Sandwich Bread", "Modern", 35, 40, "400 g", "Classic fluffy white sandwich loaf."),
            ("The Baker's Dozen Sourdough Bread", "The Baker's Dozen", 110, 130, "250 g", "Artisan fermented sourdough loaf."),
            ("Fresh Mumbai Ladi Pav", "LocalBake", 25, 30, "6 pcs pack", "Fluffy, pillowy soft pav for bhaji and vada."),
            ("Milky Mist Paneer", "Milky Mist", 92, 99, "200 g", "Vacuum sealed fresh soft malai paneer."),
            ("Amul Fresh Cream 25% Fat", "Amul", 62, 65, "250 ml", "Whipped dessert and gravies topping cream."),
            ("Nestle Everyday Dairy Whitener", "Nestle", 120, 130, "200 g pouch", "Rich dairy powder for instant tea and coffee.")
        ]
    },
    {
        "category": "Snacks & Munchies",
        "subcategories": ["Chips & Crisps", "Namkeen & Bhujia", "Popcorn & Puffs", "Roasted Nuts & Makhana"],
        "items": [
            ("Lay's India's Magic Masala", "Lay's", 20, 20, "50 g", "Spicy ridged potato chips with desi spices."),
            ("Lay's American Style Cream & Onion", "Lay's", 20, 20, "50 g", "Crispy savory chips with rich onion cream."),
            ("Doritos Nacho Cheese Tortilla Chips", "Doritos", 35, 40, "60 g", "Crunchy corn tortilla chips with bold cheddar."),
            ("Kurkure Masala Munch", "Kurkure", 20, 20, "75 g", "Crispy spicy crunchy fried corn curls."),
            ("Haldiram's Aloo Bhujia", "Haldiram's", 48, 55, "150 g", "Tangy minty spiced potato sev namkeen."),
            ("Haldiram's Bhujia Sev", "Haldiram's", 52, 60, "200 g", "Traditional Bikaneri spiced moth bean sev."),
            ("Bikaji Moong Dal Namkeen", "Bikaji", 40, 48, "180 g", "Salted crispy fried split yellow lentils."),
            ("ACT II Instant Popcorn Butter Lovers", "ACT II", 35, 40, "85 g", "Microwave instant movie style butter popcorn."),
            ("Farmley Roasted & Salted Makhana", "Farmley", 110, 140, "100 g", "Crunchy foxnuts seasoned with Himalayan salt."),
            ("Pringles Original Potato Crisps", "Pringles", 99, 115, "107 g can", "Stackable savory crispy potato wafers."),
            ("4700BC Gourmet Caramel Popcorn", "4700BC", 75, 90, "125 g tin", "Artisan popcorn coated in golden crunchy caramel."),
            ("Tongue Twisters Banana Chips", "KeralaCrunch", 45, 55, "100 g", "Coconut oil fried crispy banana chips."),
            ("Bingo! Mad Angles Achaari Masti", "Bingo!", 20, 20, "66 g", "Triangle corn snack with tangy pickle masala."),
            ("Uncle Chipps Spicy Treat", "Uncle Chipps", 20, 20, "50 g", "Classic Indian nostalgic ridged potato chips.")
        ]
    },
    {
        "category": "Instant & Frozen Food",
        "subcategories": ["Noodles & Pasta", "Frozen Snacks", "Ready to Eat", "Soups & Purees"],
        "items": [
            ("Maggi 2-Minute Masala Noodles", "Nestle", 14, 14, "70 g", "India's favorite instant noodles with tastemaker."),
            ("Maggi Special Masala Noodles 4-Pack", "Nestle", 68, 72, "280 g", "Blend of 20 roasted Indian herbs and spices."),
            ("Yippee! Magic Masala Noodles", "Sunfeast", 15, 16, "65 g", "Non-sticky round block savory noodles."),
            ("Bambino Roasted Vermicelli", "Bambino", 32, 40, "400 g", "Hard wheat semolina roasted sevai."),
            ("Barilla Penne Rigate Italian Pasta", "Barilla", 165, 195, "500 g", "Durum wheat semolina authentic Italian pasta."),
            ("McCain French Fries Crispy", "McCain", 115, 135, "420 g", "Restaurant style golden crispy potato fries."),
            ("McCain Smiles Mashed Potato Shapes", "McCain", 125, 145, "375 g", "Fun crispy smiling potato shapes."),
            ("Prasuma Pork/Chicken Momos", "Prasuma", 195, 240, "10 pcs (250g)", "Juicy authentic steamed momos with spicy dip."),
            ("Sumeru Green Peas Frozen", "Sumeru", 75, 95, "500 g", "Sweet tender IQF frozen green peas."),
            ("Knorr Classic Mixed Vegetable Soup", "Knorr", 42, 50, "43 g", "Warm hearty instant vegetable soup."),
            ("MTR Ready to Eat Paneer Butter Masala", "MTR", 115, 135, "300 g", "Heat and eat restaurant style paneer gravy."),
            ("Ching's Secret Schezwan Chutney", "Ching's", 78, 85, "250 g bottle", "Spicy fiery dip and stir-fry sauce.")
        ]
    },
    {
        "category": "Cold Drinks & Juices",
        "subcategories": ["Soft Drinks", "Fruit Juices", "Energy Drinks", "Mineral & Sparkling Water"],
        "items": [
            ("Coca-Cola Original Taste", "Coca-Cola", 40, 40, "750 ml bottle", "Refreshing chilled cola beverage."),
            ("Coca-Cola Zero Sugar Can", "Coca-Cola", 40, 40, "300 ml can", "Great cola taste with zero sugar and calories."),
            ("Thums Up Strong Taste", "Thums Up", 40, 40, "750 ml bottle", "Toofani strong fizzy cola drink."),
            ("Sprite Clear Lime Sparkling Drink", "Sprite", 40, 40, "750 ml bottle", "Crisp, clean lemon-lime carbonated soda."),
            ("Red Bull Energy Drink", "Red Bull", 125, 125, "250 ml can", "Vitalizes body and mind with taurine and B-vitamins."),
            ("Monster Energy Drink Ultra", "Monster", 115, 125, "350 ml can", "Zero sugar smooth citrus energy punch."),
            ("Real Fruit Power Mixed Fruit Juice", "Real", 115, 130, "1 L tetra", "Blend of 9 farm fresh orchard fruits."),
            ("Tropicana 100% Orange Juice", "Tropicana", 125, 145, "1 L tetra", "Pure freshly squeezed orange juice, no added sugar."),
            ("Paper Boat Aamras Mango Drink", "Paper Boat", 32, 35, "200 ml pouch", "Rich nostalgic Alphonso mango pulp juice."),
            ("Raw Pressery Coconut Water", "Raw Pressery", 70, 80, "200 ml bottle", "Pure cold-pressed tender coconut water."),
            ("Bisleri Packaged Drinking Water", "Bisleri", 20, 20, "1 L bottle", "Mineral water with added minerals and ozone treated."),
            ("Schweppes Tonic Water", "Schweppes", 55, 60, "300 ml can", "Crisp effervescent tonic for craft mixers."),
            ("Appy Fizz Sparkling Apple Juice", "Appy", 38, 40, "600 ml", "Bubbly sparkling crisp apple drink.")
        ]
    },
    {
        "category": "Bakery & Biscuits",
        "subcategories": ["Cookies & Biscuits", "Cakes & Muffins", "Rusk & Khari", "Gourmet Breads"],
        "items": [
            ("Parle-G Gold Glucose Biscuits", "Parle", 20, 20, "200 g", "India's favorite teatime energy biscuit."),
            ("Britannia Good Day Butter Cookies", "Britannia", 30, 35, "200 g", "Rich buttery cookies loaded with cashews."),
            ("Cadbury Oreo Original Chocolate Sandwich", "Oreo", 35, 40, "120 g", "Rich chocolate cookie with sweet vanilla cream."),
            ("Sunfeast Dark Fantasy Choco Fills", "Dark Fantasy", 40, 45, "100 g", "Crisp chocolate biscuit filled with molten chocolate."),
            ("Britannia Bourbon Chocolate Creams", "Britannia", 30, 35, "150 g", "Chocolate sandwich biscuit topped with crystal sugar."),
            ("Britannia Milk Bikis", "Britannia", 25, 28, "150 g", "Calcium and milk fortified crunchy biscuits."),
            ("Britannia Toastea Premium Bake Rusk", "Britannia", 45, 50, "300 g", "Crispy cardamom flavored crunchy dip rusk."),
            ("Winkies Swiss Roll Chocolate", "Winkies", 35, 40, "4 pcs pack", "Soft sponge cake rolled with rich creamy filling."),
            ("The Baker's Dozen Banana Walnut Cake", "The Baker's Dozen", 145, 169, "150 g", "Moist artisan tea cake with banana and walnuts."),
            ("Hide & Seek Chocolate Chip Biscuits", "Parle", 30, 35, "120 g", "Crunchy cookies studded with dark chocolate chips."),
            ("Haldiram's Plain Khari Puff", "Haldiram's", 55, 65, "200 g", "Flaky layered crunchy teatime snack.")
        ]
    },
    {
        "category": "Tea, Coffee & Beverages",
        "subcategories": ["Tea Bags & Leaves", "Instant Coffee", "Ground Coffee", "Health Drinks"],
        "items": [
            ("Tata Tea Premium Desh Ki Chai", "Tata Tea", 145, 160, "500 g pouch", "Rich blend of big CTC leaves and fine aroma."),
            ("Red Label Strong Blend Black Tea", "Brooke Bond", 155, 175, "500 g pouch", "Taste of togetherness with natural flavor."),
            ("Wagh Bakri Premium CTC Tea", "Wagh Bakri", 160, 180, "500 g pouch", "Strong consistency and aromatic brew."),
            ("Tetley Pure Green Tea Bags", "Tetley", 175, 210, "50 tea bags", "Antioxidant rich refreshing soothing green tea."),
            ("Nescafe Classic Instant Coffee", "Nescafe", 165, 185, "100 g jar", "Signature rich roasted coffee aroma."),
            ("Nescafe Gold Pure Soluble Coffee", "Nescafe", 399, 450, "100 g jar", "Crafted with mountain grown arabica beans."),
            ("Bru Instant Coffee Chicory Mix", "Bru", 125, 140, "100 g pouch", "Rich roasted coffee blended with chicory."),
            ("Sleepy Owl Cold Brew Coffee Hazelnut", "Sleepy Owl", 135, 160, "Pack of 3 brew bags", "Smooth 24-hour slow steeped cold brew."),
            ("Horlicks Classic Malt Health Drink", "Horlicks", 265, 295, "500 g refill", "Clinically proven for stronger, taller growth."),
            ("Cadbury Bournvita Pro-Health Drink", "Cadbury", 245, 275, "500 g refill", "Fortified chocolate malt beverage mix."),
            ("Complan Royale Chocolate Nutrition Drink", "Complan", 285, 320, "500 g refill", "34 vital nutrients with 100% milk protein.")
        ]
    },
    {
        "category": "Atta, Rice & Dals",
        "subcategories": ["Flours & Atta", "Basmati & Daily Rice", "Lentils & Pulses", "Cooking Oils & Ghee"],
        "items": [
            ("Aashirvaad Shudh Chakki Atta", "Aashirvaad", 210, 235, "5 kg bag", "100% whole wheat stone ground roti flour."),
            ("Fortune Chakki Fresh Atta", "Fortune", 195, 220, "5 kg bag", "Soft and nutritious whole wheat flour."),
            ("Daawat Rozana Super Basmati Rice", "Daawat", 385, 450, "5 kg bag", "Aromatic long grain daily basmati rice."),
            ("India Gate Classic Basmati Rice", "India Gate", 240, 275, "1 kg pouch", "Aged exotic long grain royal rice."),
            ("Tata Sampann Unpolished Toor Dal", "Tata Sampann", 145, 165, "1 kg pouch", "Rich in protein, unpolished arhar dal."),
            ("Tata Sampann Yellow Moong Dal Split", "Tata Sampann", 135, 155, "1 kg pouch", "Quick cooking nutritious light lentil."),
            ("Organic Tattva Kabuli Chana", "Organic Tattva", 160, 185, "1 kg pack", "Large certified organic white chickpeas."),
            ("Fortune Sunlite Refined Sunflower Oil", "Fortune", 145, 160, "1 L pouch", "Light and healthy cooking oil with vitamins."),
            ("Fortune Kachi Ghani Pure Mustard Oil", "Fortune", 155, 175, "1 L bottle", "Traditional cold pressed pungent mustard oil."),
            ("Amul Pure Ghee Jar", "Amul", 310, 335, "500 ml jar", "Golden granular aromatic cow milk ghee."),
            ("Tata Salt Vacuum Evaporated Iodised", "Tata", 28, 28, "1 kg pack", "Desh ka namak with essential iodine."),
            ("Madhur Pure & Hygienic Sugar", "Madhur", 52, 60, "1 kg pack", "Refined sulphur-free sparkling white sugar crystals.")
        ]
    },
    {
        "category": "Masalas & Dry Fruits",
        "subcategories": ["Whole Spices", "Blended Spices", "Dry Fruits & Seeds", "Cooking Pastes"],
        "items": [
            ("Everest Garam Masala Powder", "Everest", 78, 88, "100 g carton", "Warm aromatic blend of 13 roasted spices."),
            ("Catch Turmeric Powder (Haldi)", "Catch", 42, 50, "200 g pouch", "High curcumin rich golden yellow spice."),
            ("MDH Deggi Mirch Red Chilli Powder", "MDH", 95, 110, "100 g carton", "Vibrant natural red color with mild heat."),
            ("Catch Coriander Powder (Dhaniya)", "Catch", 45, 52, "200 g pouch", "Fresh aroma stone ground green coriander."),
            ("Happilo 100% Natural California Almonds", "Happilo", 399, 525, "500 g pouch", "Crunchy sweet premium badam nuts."),
            ("Nutraj Premium Whole Cashews (Kaju)", "Nutraj", 420, 560, "500 g pouch", "Rich buttery large W320 cashew nuts."),
            ("Happilo Premium Green Raisins (Kishmish)", "Happilo", 149, 199, "250 g pouch", "Sweet sun-dried juicy golden raisins."),
            ("Farmley Premium Walnut Kernels (Akhrot)", "Farmley", 360, 480, "250 g pack", "Omega-3 rich vacuum packed crisp walnuts."),
            ("Dabur Hommade Ginger Garlic Paste", "Dabur", 48, 55, "200 g pouch", "Thick aromatic fresh kitchen culinary paste."),
            ("Tata Sampann Kasuri Methi", "Tata Sampann", 28, 35, "25 g box", "Sun-dried fragrant fenugreek leaves.")
        ]
    },
    {
        "category": "Cleaning & Household",
        "subcategories": ["Laundry & Detergents", "Dishwashing", "Surface Cleaners", "Disposables & Bins"],
        "items": [
            ("Surf Excel Easy Wash Detergent Powder", "Surf Excel", 145, 160, "1 kg pack", "Super fine powder that dissolves quickly."),
            ("Ariel Matic Front Load Liquid Detergent", "Ariel", 250, 290, "1 L bottle", "Tough stain removal with fresh fragrance."),
            ("Comfort After Wash Fabric Conditioner", "Comfort", 199, 235, "860 ml bottle", "Leaves clothes smelling sweet and soft."),
            ("Vim Lemon Dishwash Liquid Gel", "Vim", 99, 115, "500 ml bottle", "One spoon cleans whole sink of oily utensils."),
            ("Pril Lime Liquid Dishwash", "Pril", 110, 125, "425 ml bottle", "Active power grease-cutting lime formula."),
            ("Lizol Disinfectant Surface Cleaner Citrus", "Lizol", 195, 220, "1 L bottle", "Kills 99.9% germs, floor cleaner."),
            ("Colin Glass and Surface Cleaner", "Colin", 95, 105, "500 ml spray", "Streak-free shine on mirrors and glass."),
            ("Harpic Power Plus Disinfectant Toilet Cleaner", "Harpic", 185, 205, "1 L bottle", "10x better stain and limescale removal."),
            ("Good Knight Gold Flash Liquid Vaporizer", "Good Knight", 78, 85, "45 ml refill", "Fast action mosquito repellent system."),
            ("Origami Kitchen Towel Tissue Roll", "Origami", 99, 120, "2 ply 2 rolls", "Super absorbent kitchen paper towels."),
            ("Shalimar Premium Garbage Bags Medium", "Shalimar", 85, 110, "30 bags roll", "Oxo-biodegradable sturdy waste bags.")
        ]
    },
    {
        "category": "Personal Care",
        "subcategories": ["Soaps & Body Wash", "Hair Care", "Oral Hygiene", "Skincare & Deos"],
        "items": [
            ("Dettol Original Germ Protection Bathing Soap", "Dettol", 145, 165, "Pack of 4 (75g each)", "Trusted everyday antiseptic bathing bar."),
            ("Dove Cream Beauty Bathing Bar", "Dove", 180, 205, "Pack of 3 (100g each)", "1/4 moisturizing cream for glowing skin."),
            ("Pears Pure and Gentle Glycerine Soap", "Pears", 160, 185, "Pack of 3 (100g each)", "Natural oils and pure glycerine bar."),
            ("Head & Shoulders Cool Menthol Anti-Dandruff", "Head & Shoulders", 240, 280, "340 ml bottle", "Cleanses scalp and prevents dandruff."),
            ("L'Oreal Paris Total Repair 5 Shampoo", "L'Oreal", 270, 310, "360 ml bottle", "Repairs damaged and weak dry hair."),
            ("Colgate Total Antibacterial Toothpaste", "Colgate", 135, 155, "150 g tube", "12-hour antibacterial whole mouth defense."),
            ("Sensodyne Fresh Mint Sensitive Toothpaste", "Sensodyne", 165, 190, "150 g tube", "Clinically proven daily sensitivity relief."),
            ("Nivea Men Fresh Active Deodorant Spray", "Nivea", 175, 225, "150 ml can", "Long-lasting freshness with ocean extracts."),
            ("Vaseline Intensive Care Deep Moisture Lotion", "Vaseline", 245, 299, "400 ml bottle", "Pure oat extract for 48-hour hydration."),
            ("Parachute 100% Pure Coconut Hair Oil", "Parachute", 110, 120, "300 ml bottle", "Natural deep nourishing hair elixir.")
        ]
    },
    {
        "category": "Baby Care",
        "subcategories": ["Diapers & Wipes", "Baby Food", "Baby Skin & Bath"],
        "items": [
            ("Pampers All Round Protection Pants (M)", "Pampers", 499, 649, "Pack of 34 diapers", "Anti-rash blanket with 12 hour leak guard."),
            ("Huggies Wonder Pants Diaper (L)", "Huggies", 549, 699, "Pack of 32 diapers", "Bubble bed cushion technology."),
            ("Johnson's Baby Gentle Cleansing Wipes", "Johnson's", 165, 210, "Pack of 72 wipes", "Ultra-soft moisturizing wipes with pure water."),
            ("Nestle Cerelac Wheat Apple Baby Cereal", "Nestle", 275, 295, "300 g box", "Fortified infant cereal with iron & vitamins."),
            ("Sebamed Baby Gentle Wash", "Sebamed", 399, 450, "200 ml bottle", "pH 5.5 extra mild bath formula."),
            ("Johnson's Baby Daily Moisturizing Powder", "Johnson's", 185, 210, "400 g pack", "Classic fragrance absorbent soft powder.")
        ]
    },
    {
        "category": "Pet Supplies",
        "subcategories": ["Dog Food", "Cat Food", "Pet Care & Accessories"],
        "items": [
            ("Pedigree Adult Chicken & Vegetables", "Pedigree", 350, 410, "1.2 kg bag", "Complete balanced nutrition for adult dogs."),
            ("Drools Adult Chicken and Egg Dry Dog Food", "Drools", 299, 360, "1.2 kg bag", "Real chicken protein and shiny coat formula."),
            ("Whiskas Ocean Fish Adult Dry Cat Food", "Whiskas", 220, 260, "450 g bag", "Omega 3 & 6 with zinc for healthy vision."),
            ("Sheba Premium Wet Cat Food Tuna Fillet", "Sheba", 85, 99, "85 g pouch", "Tender succulent fish flakes in gravy."),
            ("Emily Pets Lavender Clumping Cat Litter", "Emily Pets", 380, 450, "5 L bag", "Fast odor control and quick clumping.")
        ]
    },
    {
        "category": "Pharma & Wellness",
        "subcategories": ["First Aid & Pain", "Digestive & Cold", "Health Supplements"],
        "items": [
            ("Dettol Antiseptic Disinfectant Liquid", "Dettol", 145, 160, "250 ml bottle", "First aid and wound antiseptic solution."),
            ("Volini Pain Relief Gel Spray", "Volini", 125, 145, "55 g can", "Quick absorption for joint and back pain."),
            ("Eno Fruit Salt Lemon Digestive Antacid", "Eno", 52, 58, "100 g bottle", "Relieves acidity in just 6 seconds."),
            ("Pudina Hara Active Pearls", "Dabur", 28, 32, "Pack of 10 pearls", "Natural relief from stomach ache and gas."),
            ("Himalaya Liv.52 Herbal Liver Support", "Himalaya", 160, 185, "100 tablets", "Herbal liver detoxifier and appetite booster."),
            ("HealthKart HK Vitals Multivitamin", "HealthKart", 349, 499, "60 tablets bottle", "With zinc, vitamin C, D3 and ginseng extracts."),
            ("Fast&Up Charge Natural Vitamin C & Zinc", "Fast&Up", 299, 390, "20 effervescent tablets", "Immunity boosting orange fizzy drink tablets.")
        ]
    }
]

# Modifiers & variants to realistically scale up to 1,000+ unique SKUs
PACK_VARIANTS = [
    ("Saver Pack", 1.85, 2.0, "Value Pack", "Super Saver"),
    ("Family Pack", 2.6, 2.9, "Combo Pack", "Family Deal"),
    ("Trial Pack", 0.55, 0.6, "Mini Pack", "Introductory"),
    ("Twin Pack (Buy 1 Get 1 20% Off)", 1.75, 2.0, "Pack of 2", "Trending"),
    ("Party Box", 3.2, 3.7, "Jumbo Pack", "Bestseller"),
    ("Organic Reserve", 1.35, 1.45, "Special Harvest", "Organic Certified"),
    ("Diet Edition", 1.1, 1.2, "Zero Guilt", "Healthy Choice"),
    ("Chef's Special Edition", 1.25, 1.4, "Gourmet Edition", "Top Rated")
]

TAGS_POOL = ["Bestseller", "Trending", "Super Saver", "10 MINS", "Fresh Catch", "High Protein", "Organic", "Chef's Choice", "Popular"]

def generate_full_catalog():
    """Generates over 1,000 realistic products with authentic pricing, units, and categories."""
    products = []
    
    # 1. First add all curated blueprint items
    for cat_data in CATALOG_BLUEPRINT:
        cat_name = cat_data["category"]
        subcats = cat_data["subcategories"]
        img_pool = CATEGORY_IMAGES.get(cat_name, CATEGORY_IMAGES["Dairy, Bread & Eggs"])
        
        for item in cat_data["items"]:
            name, brand, price, mrp, unit, desc = item
            subcat = random.choice(subcats)
            discount = int(round((1 - (price / mrp)) * 100)) if mrp > price else 0
            rating = round(random.uniform(4.2, 4.9), 1)
            rating_count = random.randint(45, 1850)
            img = random.choice(img_pool)
            badge = random.choice(TAGS_POOL)
            
            products.append({
                "name": name,
                "brand": brand,
                "category": cat_name,
                "subcategory": subcat,
                "price": float(price),
                "mrp": float(mrp),
                "discount_pct": discount,
                "unit": unit,
                "rating": rating,
                "rating_count": rating_count,
                "image_url": img,
                "in_stock": 1,
                "delivery_eta": f"{random.randint(8, 12)} MINS",
                "badge": badge,
                "description": desc
            })
            
    # 2. Expand systematically with realistic brand variants & sizes until > 1050 items
    seed_idx = 0
    target_count = 1050
    total_blueprints = sum(len(c["items"]) for c in CATALOG_BLUEPRINT)
    
    while len(products) < target_count:
        for cat_data in CATALOG_BLUEPRINT:
            if len(products) >= target_count:
                break
            cat_name = cat_data["category"]
            subcats = cat_data["subcategories"]
            img_pool = CATEGORY_IMAGES.get(cat_name, CATEGORY_IMAGES["Dairy, Bread & Eggs"])
            
            for item in cat_data["items"]:
                if len(products) >= target_count:
                    break
                
                name, brand, base_price, base_mrp, base_unit, base_desc = item
                var_suffix, price_mult, mrp_mult, unit_mod, tag_mod = PACK_VARIANTS[seed_idx % len(PACK_VARIANTS)]
                seed_idx += 1
                
                var_name = f"{name} ({var_suffix})"
                var_price = round(base_price * price_mult, 0)
                var_mrp = round(max(base_mrp * mrp_mult, var_price * 1.15), 0)
                discount = int(round((1 - (var_price / var_mrp)) * 100))
                rating = round(random.uniform(4.0, 4.9), 1)
                rating_count = random.randint(20, 950)
                subcat = random.choice(subcats)
                img = random.choice(img_pool)
                
                products.append({
                    "name": var_name,
                    "brand": brand,
                    "category": cat_name,
                    "subcategory": subcat,
                    "price": float(var_price),
                    "mrp": float(var_mrp),
                    "discount_pct": discount,
                    "unit": f"{base_unit} · {unit_mod}",
                    "rating": rating,
                    "rating_count": rating_count,
                    "image_url": img,
                    "in_stock": 1 if random.random() > 0.05 else 0, # 95% in stock
                    "delivery_eta": f"{random.randint(8, 12)} MINS",
                    "badge": tag_mod,
                    "description": f"{base_desc} Special {var_suffix} curated for quick home delivery."
                })

    return products

def seed_products_if_empty():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM products")
    row = cursor.fetchone()
    current_count = row["count"] if row else 0

    if current_count < 1000:
        print(f"Catalog currently has {current_count} products. Generating 1000+ products...")
        cursor.execute("DELETE FROM products")
        products = generate_full_catalog()
        
        insert_query = """
        INSERT INTO products (
            name, brand, category, subcategory, price, mrp, discount_pct,
            unit, rating, rating_count, image_url, in_stock, delivery_eta, badge, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        data_tuples = [
            (
                p["name"], p["brand"], p["category"], p["subcategory"],
                p["price"], p["mrp"], p["discount_pct"], p["unit"],
                p["rating"], p["rating_count"], p["image_url"],
                p["in_stock"], p["delivery_eta"], p["badge"], p["description"]
            )
            for p in products
        ]
        
        cursor.executemany(insert_query, data_tuples)
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) as count FROM products")
        new_count = cursor.fetchone()["count"]
        print(f"Successfully seeded {new_count} products into database!")
    else:
        print(f"Database already contains {current_count} products.")
        
    conn.close()

if __name__ == "__main__":
    from app.database import init_db
    init_db()
    seed_products_if_empty()
