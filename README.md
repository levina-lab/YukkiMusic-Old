This is a Old Yukki Music source code, newest version is placed here: https://github.com/NotReallyShikhar/YukkiMusicBot

Full Credit is given to [@TeamYukki](https://t.me/OfficialYukki)

Don't ask about is it a clone / kang or not, Use your mind to know about it !

### String Session

[![GenerateString](https://img.shields.io/badge/repl.it-generateString-yellowgreen)](https://replit.com/@levinalab/StringSession#main.py)

### Deploy To Heroku 

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/levina-lab/YukkiMusic-Old)

## VPS Deployment 📡
Get the best Quality of streaming performance by hosting it on VPS, here's the step's:

```sh
sudo apt update && apt upgrade -y
sudo apt install git curl python3-pip ffmpeg -y
pip3 install -U pip
curl -sL https://deb.nodesource.com/setup_16.x | bash -
sudo apt-get install -y nodejs
npm i -g npm
git clone https://github.com/levina-lab/YukkiMusic-Old # clone the repo.
cd YukkiMusic-Old
pip3 install -U -r requirements.txt
cp sample.env .env # use vim to edit ENVs
vim .env # fill up the ENVs (Steps: press i to enter in insert mode then edit the file. Press Esc to exit the editing mode then type :wq! and press Enter key to save the file).
python3 -m Yukki # run the bot.

# continue the host with screen or anything else, thanks for reading.
```
