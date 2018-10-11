# Wikipediaの文章から頻出単語を抜き出す

import sys
import os
from glob import glob
from collections import Counter

import MeCab


def main():
    """
    コマンドライン引数で指定したディレクトリ内のファイルを読み込んで、頻出単語を商事する
    """

    input_dir = "./../artisles"

    tagger = MeCab.Tagger('')
    tagger.parse('')  # parseToNode()の不具合を回避するために必要。

    # 単語の頻度を格納するCounterオブジェクトを作成する
    # Counterクラスはdictを継承しており、値としてキーの出現回数を保持する
    frequency = Counter()
    count_processed = 0

    # glob()でワイルドカードにマッチするファイルのリストを取得し、マッチした全てのファイルを処理する
    for path in glob(os.path.join(input_dir, '*', 'wiki_*')):
        print('Processing {0}...'.format(path), file=sys.stderr)

        with open(path) as file:  # ファイルを開く
            for content in iter_docs(file):  # ファイル内の全記事について反復処理をする
                tokens = get_tokens(tagger, content)  # ページから名詞のリストを取得する

                # Counterのupdate()メソッドにリストなどの反復可能なオブジェクトを指定すると、
                # リストに含まれる値の出現回数を一度に増やせる
                frequency.update(tokens)

                # 10000件ごとに進捗を表示
                count_processed += 1
                if count_processed % 10000 == 0:
                    print('{0} documents were processed.'.format(count_processed), file=sys.stderr)

    # 全記事の処理が完了したら上位30位の名詞と出現回数を表示する
    for token, count in frequency.most_common(30):
        print(token, count)


def iter_docs(file):
    """
    ファイルオブジェクトを読み込んで、記事の中身(開始タグと終了タグの間のテキスト)を順に返すジェネレーター関数
    """

    for line in file:
        if line.startswith('<doc '):
            buffer = []  # 開始タグが見つかったらバッファを初期化する
        elif line.startswith('</doc>'):
            content = ''.join(buffer)  # 終了タグが見つかったらバッファの中身を結合してyieldする
            yield content
        else:
            buffer.append(line)  # 開始タグ・終了タグ以外の行はバッファに追加する


def get_tokens(tagger, content):
    """
    文書内に出現した名詞のリストを取得する関数
    """
    tokens = []  # この記事で出現した名詞を格納するリスト

    node = tagger.parseToNode(content)
    while node:

        # node.featureはカンマで区切られた文字列なのでsplit()で分割して
        # 最初の2項目をcategoryとsub_categoryに代入する
        category, sub_category = node.feature.split(',')[:2]

        # 固有名詞または一般名詞の場合のみtokensに追加する
        # 「〜を」や「。」などが抜き出されないようにするため
        if category == '名詞' and sub_category in ('固有名詞', '一般'):
            tokens.append(node.surface)
        node = node.next

    return tokens


if __name__ == '__main__':
    main()
