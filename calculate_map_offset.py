import math

# --- CONFIGURATION ---
METERS_PER_NM = 1852
HEX_NM = 20
HEX_RADIUS = HEX_NM * METERS_PER_NM

# Map setup
# Min X: -10000000.000
# Max X: 8000000.000
# Min Y: -7750000.000
# Max Y: 6750000.000

# List of real-world locations in Meters (relative to your current GIS (0,0))
# Example: [ (x1, y1), (x2, y2), ... ]
LOCATIONS_METERS = [
    # JAPAN
    (8367692.31, 4648717.95), # Tokyo
    (7903962.70, 4684125.87), # Osaka
    (8052447.55, 4655571.10), # Nagoya
    (7371249.514374518,4704423.562548563), # Fukuoka
    (7317947.261072264,4960464.743589744), # Kagoshima
    (8547706.390831392,4360338.480963482), # Sendai
    (8357341.2004662035,4356531.177156177), # Niigata
    (8602436.383061385,4032910.353535354), # Aomori
    (8729029.234654237,3774965.520590521), # Sapporo
    (8990781.371406374,3820653.1662781667), # Kushiro
    
    # KOREA
    (7182787.975912979,4126665.2097902102), # Seoul
    (7158040.501165504,3921070.804195805),# Pyongyang
    (7294627.525252528,4490262.723387724), # Busan
    
    # MANCHURIA
    (6779213.772338775,3811134.9067599075), # Dalian
    
    # CHINA
    # Beijing
    (6390868.783993786,4756298.076923078),# Shanghai
    # Changsha
    # Zhengzhou
    # Xi'an
    # Chongqing
    # Guangzhou
    # Fuzhou
    (4585730.86635587,6038883.547008547), # Sanya
    (5256292.249417252,5669575.0777000785), # Hong Kong
    
    # TAIWAN
    # Taipei
    (5938751.4568764595,5837572.358197358), # Kaohsiung
    
    # BRITISH EMPIRE
    (3440208.3333333367,8204763.5003885), # Singapore
    # Kuala Lumpur
    # Brunei
    # Rangoon
    # Mandalay
    # Colombo
    (10302183.372183371,10246406.37140637), # Tulagi
    (9771064.49106449,9983702.408702409), # Shortlands
    
    # AUSTRALIA
    # Sydney
    # Melbourne
    (6695914.509044696,10535872.410799991),# Darwin
    # Perth
    # Adelaide
    # Cooktown
    # Port Moresby
    (9321064.97668998,9642020.687645687), # Rabaul
    (8667422.299922299,9917074.592074592), # Lae
    (9098123.543123541,10375378.787878787), # Milne Bay
    
    # NEW ZEALAND
    # Auckland
    # Wellington
    
    # CANADA
    (16374886.523271045,1376792.0370191138), # Vancouver
    (16438400.425905617,1479819.5747471566), # Victoria
    
    # BRITISH RAJ
    # Dhaka
    # Chennai
    # Mumbai
    # Delhi
    
    # USA
    (16590692.57819777,1512562.3874899694), # Seattle
    (16792479.67998487,1763082.9780105597), # Portland
    (17562765.31114983,2676605.5568326334), # San Francisco
    # Los Angeles
    # San Diego
    (15051685.091868913,6176561.800127972), # Honolulu
    (13690288.53779374,1156960.2118877943), # Anchorage
    
    # PHILLIPINES
    (5757785.547785548,6862284.382284382), # Manila
    (6149752.1945455205,7947349.448072469), # Davao
    (6012303.807303808,7491822.066822067), # Cebu
    (5938251.748251748,6397412.587412587), # Aparri
    
    # DUTCH EAST INDIES
    # Jakarta
    (4448667.929292932,9621556.42968143), # Surabaya
    # Makassar
    # Jayapura
    # Balikpapan
    
    # USSR
    # Vladivostok
    # Khabarovsk
    # Petropavlovsk-Kamtchatsky
    
    # ISLANDS
    (8505974.809984334,7427620.999723077), # Guam
    (9298012.980147505,8231081.081308158), # Truk
    (7228509.250162103,8033532.961528714), # Babeldaob
    (10068091.082471265,8313216.039393617), # Ponape
    # Midway
    # Suva
    # Noumea
    (11154430.520940045,11032661.79226387)# Luganville
    # Port-Vila
    # Tarawa
]

def get_hex_center(x, y, radius):
    """
    Calculates the nearest hex center for a given point (x, y) 
    assuming a Pointy-Top hex grid.
    """
    # Inverse of the Pointy-top hex-to-pixel matrix
    q = (math.sqrt(3)/3 * x - 1/3 * y) / radius
    r = (2/3 * y) / radius
    
    # Hex rounding logic
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    
    dq = abs(rq - q)
    dr = abs(rr - r)
    ds = abs(rs - s)
    
    if dq > dr and dq > ds:
        rq = -rr - rs
    elif dr > ds:
        rr = -rq - rs
    
    # Convert axial (rq, rr) back to world meters
    center_x = radius * math.sqrt(3) * (rq + rr/2.0)
    center_y = radius * 1.5 * rr
    return center_x, center_y

def calculate_total_error(offset_x, offset_y):
    """Calculates average distance from points to nearest hex center."""
    total_dist = 0
    for px, py in LOCATIONS_METERS:
        # Apply the proposed map shift
        shifted_x = px - offset_x
        shifted_y = py - offset_y
        
        cx, cy = get_hex_center(shifted_x, shifted_y, HEX_RADIUS)
        dist = math.sqrt((shifted_x - cx)**2 + (shifted_y - cy)**2)
        total_dist += dist
    return total_dist / len(LOCATIONS_METERS)

def optimize():
    best_error = float('inf')
    best_offset = (0, 0)
    
    # Search space: One full hex width/height is enough to cover all possibilities
    search_width = int(HEX_RADIUS * math.sqrt(3))
    search_height = int(HEX_RADIUS * 1.5)
    
    print(f"Optimizing alignment for {len(LOCATIONS_METERS)} points...")
    
    # Grid search (Step size can be increased for speed or decreased for precision)
    step = 60 # meters
    for ox in range(0, search_width, step):
        for oy in range(0, search_height, step):
            err = calculate_total_error(ox, oy)
            if err < best_error:
                best_error = err
                best_offset = (ox, oy)
                
    print("--- OPTIMIZATION COMPLETE ---")
    print(f"Minimal Avg Distance: {best_error/1852:.2f} NM")
    print(f"Shift GIS Top-Left X by: {best_offset[0]:.2f} meters")
    print(f"Shift GIS Top-Left Y by: {best_offset[1]:.2f} meters")
    print("\nAction: In your GIS software, subtract these values from your ")
    print("current export Top-Left coordinates.")

if __name__ == "__main__":
    optimize()