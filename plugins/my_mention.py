# coding: utf-8

from slackbot.bot import respond_to


@respond_to("-help")
def help_func(message):
    message.send("""\
            -help ヘルプコマンド
            -rule ルール説明
            -start ゲーム開始
            """)


@respond_to("-rule")
def rule_func(message):
    message.send("""\
            それぞれの人は全員所持金10000円でオークションを行います。
            最初に、それぞれの人が絶対に欲しい物を伝えられます。
            それは他の人と被っているかも知れませんし、被っていないかも知れません。
            他の人の欲しいものは分かりません。
            そして参加人数の回数分オークションが行われます。
            必ず一度だけ、それぞれの人の欲しいものはオークションに現れます。
            全てのオークションが終わった時点で、欲しい物を持っていない人は負けです。
            欲しい物を持っている人の中で、最も所持金が多く残っている人の勝利です。

            つまりは本命を悟られ無いようにしながら、欲しい物を安く買い取るゲームです。""")
