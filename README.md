# crowdscores_client
#The display I used can be found here from Farnell
#http://uk.farnell.com/piface/piface-control-display/i-o-board-with-lcd-display-for/dp/2344458

sudo apt-get update && sudo  apt-get upgrade -y

sudo apt-get install  python3-pifacecad -y

git clone https://github.com/martyni/crowdscores_client.git

cd crowdscores_client

sudo pip-3.2 -r requirements.txt

echo “YOUR API KEY” > ~./crowdscores

#Test the client is working

python3 -i client.py

client.get_matches()
# CTRL + d

python3 screen.py

