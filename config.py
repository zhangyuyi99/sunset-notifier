# Location — latitude and longitude are most accurate
LATITUDE  = 32.8458529
LONGITUDE = -117.2575702

# Which days to send reminders
# Options: "weekdays", "everyday", or a list like ["mon","tue","wed","thu","fri","sat"]
REMIND_DAYS = 'weekdays'

# How many minutes before sunset to notify
MINUTES_BEFORE = 5

# Notification language: "en" or "zh"
LANGUAGE = "zh"

# Notification title and message templates
# Use {sunset_time} and {minutes} as placeholders
NOTIFY_TITLE_EN   = "🌅 Sunset in {minutes} minutes"
NOTIFY_MESSAGE_EN = "Today's sunset is at {sunset_time}. Go take a look!"

NOTIFY_TITLE_ZH   = "🐸 小青蛙提醒你"
NOTIFY_MESSAGE_ZH = "今天日落时间是 {sunset_time}，还有 {minutes} 分钟，放下手里的事去看看吧！"

MESSAGES_ZH = [
    "太阳要下山了，快去看！",
    "今天的云很好看，不来会后悔的。",
    "去看日落吧，什么烦恼都暂时不重要。",
    "今天的日落是限定款，先到先得！",
    "窗外正在发生今天最美的事。",
    "日落不等人，但它愿意等你5分钟。",
    "科研可以等下继续，日落只有现在哦。",
]

MESSAGES_EN = [
    "The sun is putting on a show. Go watch it.",
    "Golden hour is here. Drop everything. Go.",
    "Best free show in town — happening right now outside your window.",
    "Today's sunset is one of a kind. So are you. Go enjoy it together.",
    "The sky is about to do something beautiful. Don't miss it.",
    "Your paper can wait 5 minutes. The sunset cannot.",
    "Mandatory sunset break. Doctor's orders. 🐸",
]
