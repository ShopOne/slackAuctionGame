# coding: utf-8

from slackbot.bot import respond_to
from slackbot.bot import default_reply
from run import client
from plugins.person import Person
from plugins.progress import Progress
import random
import time
import threading


ITEM_DICT = ["りんご", "みかん", "にんじん", "かぼちゃ",
             "ちくわ", "カモメ", "乾電池", "コショウ",
             "扇風機", "カーテン", "えんぴつ", "桃",
             "ガム", "ぶどう", "いちご", "バイク",
             "パソコン", "針金", "輪ゴム", "靴下",
             "クッション", "うどん", "お茶", "犬",
             "ゲーム", "モンブラン", "なべ", "フライパン"]
RARE_ITEM_DICT = ["風来のシレン", "青春", "10万円",
                  "PSVita", "単位"]
RARE_RATE = 0.05
FIRST_MONEY = 300
AUCTION_START_G = 1
INTERVAL = 10

now_price = 0
least_count = 0
participant = []
auction_item = []
auction_progress = 0
now_progress = Progress.FREE
occor_bid = False


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def reset():
    global participant, auction_item, auction_progress
    global now_progress
    participant = []
    auction_item = []
    auction_progress = 0
    now_progress = Progress.FREE


def end_game():
    reset()


def decrease_least():
    global least_count
    print("call" + str(time.time()))
    least_count -= 1


def auction_schedule(message):
    global least_count
    base_time = time.time()
    next_time = 0
    least_count = 3
#    occor_bid = False
    while least_count > 0:
        t = threading.Thread(target=decrease_least)
        t.start()
        next_time = ((base_time - time.time()) % INTERVAL) or INTERVAL
        time.sleep(next_time)


def start_new_auction(message):
    if auction_progress == len(auction_item):
        end_game()
        return
    global now_price
    now_price = AUCTION_START_G
    message.send("""メンションで『bid "金額"』 ("と『』不要)で入札します')
誰も入札出来ない金額になるか、一定時間経つと次へ移ります'
時間はおおよそ30秒、ただし残り時間が10秒未満の間に入札された場合は時間が延長します""")
    now_mon = "所持金\n"
    for i in range(len(participant)):
        now_mon += participant[i].name + ": " + str(participant[i].money)
        if i != len(participant):
            now_mon += "\n"
    message.send(now_mon)
    auction_schedule(message)


@default_reply()
def default_func(message):
    if now_progress == Progress.REQRUIT:
        user_name = message.user["profile"]["display_name"]
        user_id = message.body['user']
        if not (user_name in participant):
            participant.append(Person(user_id, user_name, FIRST_MONEY))
            message.reply("参加を受け付けました")
        else:
            message.reply("既に参加しています")
    else:
        message.reply("ウグゥーーーーーーーーーーッ!!!")


@respond_to(r"bid \d+")
def bid_func(message):
    if now_progress != Progress.ONGAME:
        message.send("今は何も出品していません")
        return
    text = message.body['text']
    parsed_text = text.split()
    if(len(parsed_text) != 2 and not is_integer(parsed_text[1])):
        message.send("フォーマットに不具合があります")
        return
#    bid_price = int(parsed_text[1])


@respond_to("break")
def break_func(message):
    if now_progress != Progress.FREE:
        reset()
        message.send("セッションを強制終了しました")
    else:
        message.send("何も始まっていません")


@respond_to("help")
def help_func(message):
    message.send("""\
help ヘルプコマンド
rule ルール説明
start ゲーム開始
break セッションの強制終了""")


@respond_to("ok")
def ok_func(message):
    global auction_times, participant, now_progress
    if now_progress != Progress.REQRUIT:
        message.send("確かに僕もOKだと思います")
        return
    if len(participant) == 0:
        message.send("誰も参加していません")
        return
    auction_times = len(participant) + random.randint(0, len(participant)+2)
    # 辞書サイズを超えないように
    auction_times = min(auction_times, len(RARE_ITEM_DICT + ITEM_DICT))
    auction_times = max(2, auction_times)

    use_dict = random.sample(ITEM_DICT, len(ITEM_DICT))
    use_rare = random.sample(RARE_ITEM_DICT, len(RARE_ITEM_DICT))
    dict_idx = rare_idx = 0
    for i in range(auction_times):
        if dict_idx == len(use_dict) or random.random() <= RARE_RATE:
            auction_item.append(use_rare[rare_idx])
            rare_idx += 1
        else:
            auction_item.append(use_dict[dict_idx])
            dict_idx += 1

    for i in range(len(participant)):
        participant[i].like = random.sample(auction_item, 2)
        client.chat_postMessage(
            channel=participant[i].id,
            text=str(participant[i].like)+"を落札して下さい。")
    message.send("参加者は" + str(*participant) + "です")
    now_progress = Progress.ONGAME
    start_new_auction(message)


@respond_to("start")
def start_func(message):
    global now_progress
    if(now_progress != Progress.FREE):
        message.send("今はstart出来ません")
        return

    message.send("""ゲーム参加者を募集します
参加する人はなんでも良いのでこのbotにリプライを送信して下さい。
全員参加したら、okとリプライして下さい。""")
    now_progress = Progress.REQRUIT


@respond_to("rule")
def rule_func(message):
    message.send("""\
それぞれの人は全員所持金300円でオークションを行います。
全ての人に、オークションで欲しい物が2つ決められます。
これは他の人には分からず、被っている場合もあります。
その物は、必ず1度のみオークションに出品されます。
オークションには皆にとってどうでもいい品が出品される可能性もあります。
全てのオークションが終了した時点で、欲しい物を一番多く持っている人、
同じ数だけ持っているのなら、残ったお金が多い人が勝者となります。""")
