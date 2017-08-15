# Run by launchd
# /Library/LaunchDaemons/com.user.stockanalysis.plist
# launchctl <load | unload> <path to plist file>

cd /Users/michaelstecklein/Projects/StockAnalysis2/
mkdir -p logs
sudo python main_update.py
#sudo python -W ignore main_update.py
