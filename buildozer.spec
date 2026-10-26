[app]
title = Auction App
package.name = auctionapp
package.domain = org.auction
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi

# ОЧЕНЬ ВАЖНО: Разрешаем приложению выход в интернет
android.permissions = INTERNET

orientation = portrait
fullscreen = 0
