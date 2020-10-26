#===============================================================================
#
#     CodeName    : searchKeyword_v0.py
#     Author      : Noritaka Ishizaka
#     Description : キーワード検索ヒットした動画を再生回数が多い順番でソートして
# 　　　　　　　　　　表示する。検索件数の上限が引数で指定する。
#                   また検索結果の動画がどのチャンネルからアップロードされている
#                   ものかをcsvファイルに出力する。
#
#===============================================================================
# import library
from apiclient.discovery import build
from apiclient.errors import HttpError
import argparse
import numpy as np
import pandas as pd

# Set Yotube Data API key
DEVELOPER_KEY = "YOUR API KEY !!!"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def searchKeyword(options):
    # キーワード検索処理
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                    developerKey=DEVELOPER_KEY)
    searchResults = youtube.search().list(q=options.sw,
                                        type="video",
                                        part="id,snippet",
                                        maxResults=options.max_results,
                                        order="viewCount"
                                        ).execute()
    
    # 検索結果分類処理
    videos = []
    others = []
    for searchResult in searchResults["items"]:
        if (searchResult["id"]["kind"] == "youtube#video"):
            videos.append(searchResult)
        else :
            others.append(searchResult)

    #動画、チャンネル情報整形、csvファイル出力
    videoTitles = []
    viewCounts = []
    likeCounts = []
    dislikeCounts = []
    favoriteCounts = []
    commentCounts =[]
    videoChannelTitles = []
    for video in videos:
        videoDetail = youtube.videos().list( part="statistics, snippet",
                                            id = video["id"]["videoId"]
                                            ).execute()
        channelDetail = youtube.channels().list(part="snippet", 
                                                id=videoDetail["items"][0]["snippet"]["channelId"]
                                                ).execute()
        videoChannelTitles.append(channelDetail["items"][0]["snippet"]["title"])
        videoTitles.append(videoDetail["items"][0]["snippet"]["title"])
        viewCounts.append(videoDetail["items"][0]["statistics"]["viewCount"])
        likeCounts.append(videoDetail["items"][0]["statistics"]["likeCount"])
        dislikeCounts.append(videoDetail["items"][0]["statistics"]["dislikeCount"])
        favoriteCounts.append(videoDetail["items"][0]["statistics"]["favoriteCount"])
        commentCounts.append(videoDetail["items"][0]["statistics"]["commentCount"])
        

    df_videos = pd.DataFrame({"title":videoTitles, "ViewCount":viewCounts, 
                            "channelTitle":videoChannelTitles,"likeCount":likeCounts,
                            "dislikeCount":dislikeCounts, "favoriteCount":favoriteCounts,
                            "commentCount":commentCounts})
    df_videos.to_csv("Search_result_{}.csv".format(options.sw),encoding="utf-8_sig")
    df_videos_countbyChannel = df_videos["channelTitle"].value_counts()
    df_videos_countbyChannel.to_csv("ChannelTitle_{}.csv".format(options.sw),encoding="utf-8_sig")

    return df_videos, df_videos_countbyChannel
    


if __name__ == "__main__":
    # parse Argument
    parser = argparse.ArgumentParser("search Youtube Program...")
    parser.add_argument("sw", help="search Keyword in Youtube")
    parser.add_argument("--max_results", type=int, help="max of search results",
                        default=50)
    options = parser.parse_args()

    searchKeywordResults = searchKeyword(options)
