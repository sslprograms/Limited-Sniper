import requests, threading, os, colorama, json, time, random

# Developed by ssl#8290

settings = json.loads(
    open('settings.json', 
    'r'
).read()
)['settings']

cookie = settings['cookie']
assetIds = settings['assetids']
sniperSettings = settings['sniperSettings']
blockedSellersIds = settings['blockedSellersIds']
proxies_enabled = settings['proxies']
proxies = open(
    'proxies.txt',
    'r'
).read().splitlines()

xcsrf_token = ''

def refresh_xcsrf():
    global xcsrf_token
    while True:
        with requests.session() as session:
            session.cookies['.ROBLOSECURITY'] = cookie
            xcsrf_token = session.post(
                'https://friends.roblox.com/v1/users/1/request-friendship'
            ).headers['x-csrf-token']
            print(f'- x-csrf-token set to {xcsrf_token}!')
        time.sleep(500)
    

def purchaseAssetId(ProductId, sellerPrice, sellerId):
    global xcsrf_token
    with requests.session() as session:
        session.cookies['.ROBLOSECURITY'] = cookie
        session.headers['x-csrf-token'] = xcsrf_token
        purchaseAsset = session.post(
            f"https://economy.roblox.com/v1/purchases/products/{ProductId}",
            data={
                "expectedCurrency":1,
                "expectedPrice":sellerPrice,
                "expectedSellerId":sellerId
            }
        )
        
        if purchaseAsset.status_code == 200 and purchaseAsset.json()['purchased'] == True:
            print(f'You have caught a SNIPE: ({purchaseAsset.text})')
            requests.post(
                settings['webhook'],
                json = {
                    'content':f'**SNIPE** was success! ({ProductId}) / {sellerPrice} was the seller price!'
                }
            )
        elif purchaseAsset.json()['purchased'] == False:
            print(f'- Failed to catch the SNIPE: ({purchaseAsset.text})')
            requests.post(
                settings['webhook'],
                json = {
                    'content':f'**Failed to **SNIPE** ({ProductId}) for ({sellerPrice} amount of Robux!)**'
                }
            )
    return

def checkAssetPrice():
    global xcsrf_token
    while True:
        try:
            with requests.session() as session:
                if proxies_enabled == True:
                    proxy = {'http':random.choice(proxies), 'https':random.choice(proxies)}
                else:
                    proxy = {'http':None, 'https':None}
                requestJSON = {
                    "items":[
                    ]
                }
                for asset in assetIds:
                    requestJSON['items'].append(
                        {
                            "itemType":"Asset",
                            "id":asset
                        }
                    )
                session.cookies['.ROBLOSECURITY'] = cookie
                session.headers['x-csrf-token'] = xcsrf_token
                requestAssetInfo = session.post(
                    "https://catalog.roblox.com/v1/catalog/items/details",
                    json=requestJSON,
                    proxies=proxy
                )

                if requestAssetInfo.status_code == 200:
                    
                    for blockedId in blockedSellersIds:
                        for data in requestAssetInfo.json()['data']:
                            if data['creatorTargetId'] != blockedId and data['lowestPrice'] <= sniperSettings['maxPrice'] and data['lowestPrice'] >= sniperSettings['lowPrice']:
                                threading.Thread(target=purchaseAssetId, args=(data['productId'], data['lowestPrice'], data['creatorTargetId'],)).start()
                                print('- Sent a new thread to attempt a purchase :)')
        except:
            print('- Sniper was interupted with an error! (ignoring..)')
print(str(settings) + '\n\n')
print('===========================================')
print('-> Limited Sniper is awaiting start!')
print('- Setting x-csrf-token...')
threading.Thread(target=refresh_xcsrf,).start()
time.sleep(2)
print('- Started SNIPER..')
checkAssetPrice()
