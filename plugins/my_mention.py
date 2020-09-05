# coding: utf-8

from slackbot.bot import respond_to
from slackbot.bot import default_reply
from enum import Enum
from run import client
import random


class Progress(Enum):
    FREE = "FREE"
    REQRUIT = "REQRUIT"
    ONGAME = "ONGAME"


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
now_price = 0

participant = []
participant_is_end = []
participant_id = []
participant_like = []
participant_money = []
auction_item = []
auction_progress = 0
now_progress = Progress.FREE


def reset():
    global participant, participant_like, auction_item, auction_progress
    global now_progress, participant_money
    participant = []
    participant_like = []
    participant_money = []
    auction_item = []
    auction_progress = 0
    now_progress = Progress.FREE


def end_game():
    reset()


def start_new_auction(message):
    if auction_progress == len(auction_item):
        end_game()
        return
    global now_price
    now_price = AUCTION_START_G
    message.send("""メンションで『bid "金額"』 ("と『』不要)で入札します')
誰も入札出来ない金額になるか、一定時間経つと次へ移ります'
時間はおおよそ30秒、ただし入札された後残り時間が10秒未満であれば残り10秒になります""")
    now_mon = "所持金\n"
    for i in range(len(participant)):
        now_mon += participant[i] + ": " + participant_money[i]
        if i != len(participant):
            now_mon += "\n"
    message.send(now_mon)


@default_reply()
def default_func(message):
    if now_progress == Progress.REQRUIT:
        user_name = message.user["profile"]["display_name"]
        user_id = message.body['user']
        if not (user_name in participant):
            participant.append(user_name)
            participant_id.append(user_id)
            message.reply("参加を受け付けました")
        else:
            message.reply("既に参加しています")
    else:
        message.reply("ウグゥーーーーーーーーーーッ!!!")


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
    global auction_times, participant_like, now_progress
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
        participant_money.append(FIRST_MONEY)
        participant_is_end.append(False)
        participant_like.append(random.sample(auction_item, 2))
        client.chat_postMessage(
            channel=participant_id[i],
            text=str(*participant_like)+"を落札して下さい。")
    message.send("参加者は" + str(*participant) + "です")
    now_progress = Progress.ONGAME
    start_new_auction(message)


@respond_to("start")
def start_func(message):
    global now_progress
    if(now_progress != now_progress.FREE):
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
