################################################################################
# Python Imports
################################################################################
# This is only needed for picking a randomised IP address from CHANNEL_IPS array
import random

# This is only needed for removing the new line character (\n) in upcoming event
# data (title and competition)
import re

################################################################################
# Global variables for channel
################################################################################
TITLE                           = "HD Streaming"
PREFIX                          = "/video/hdstreaming"

ART                             = "art-default.png"
ICON                            = "icon-default.png"

# Below values lifted from FilmOn plugin
USER_AGENT                      = "Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25"

# Using a referrer as the domain for login is different to the channel domain
REFERER                         = "http://news-source.tv/"

# URLs for hd-streaming site
URL_BASE                        = "http://82.80.192.2/iba_channel-511MRepeat/_definst_/smil:channel-511M.smil/playlist.m3u8"
#URL_LOGIN                       = "api/?request=login"
#URL_LIVE                        = "watch/livehds"
#URL_UPCOMING                    = "watch/upcoming-matches"

# File name parts for video URLs
#
# N.B. Suffix includes file extension .m3u8
VIDEO_PREFIX                    = "http://"
VIDEO_DIRECTORY                 = "/hls/"
VIDEO_SUFFIX                    = ".m3u8?s=6hfu0"

# IP addresses used by channel video URLs
CHANNEL_IPS                     = ["5.63.145.149",
                                    "5.63.145.189",
                                    "80.82.65.14",
                                    "80.82.65.180",
                                    "80.82.69.240",
                                    "80.82.78.62",
                                    "89.248.160.222",
                                    "89.248.171.15",
                                    "93.174.91.104",
                                    "94.102.48.81",
                                    "94.102.49.152",
                                    "146.185.28.197"]
                                    
# Global variable used to store channel list
CHANNEL_LIST                    = []

# Global variable used to store upcoming data
UPCOMING_EVENTS_LIST            = []

################################################################################
# Gets a list of channels to iterate over
################################################################################
def GetChannelList():
    # Check to see if CHANNEL_LIST is already populated, if True return it, if
    # not construct it.
    if CHANNEL_LIST:
        return CHANNEL_LIST
    else:
        # Gets the HTML source from the Live Stream URL
        CHANNEL_LIST_URL        = URL_BASE #+ URL_LIVE
        CHANNEL_LIST_SOURCE     = HTML.ElementFromURL(CHANNEL_LIST_URL)
        
        # Find the channel links in the HTML source with xPath
        CHANNELS                = CHANNEL_LIST_SOURCE.xpath("//a[@class='ch-link']")
        
        # Add each channel to CHANNEL_LIST
        for CHANNEL in CHANNELS:
            # Grab the link text, and convert from list to string
            #
            # N.B. xpath ALWAYS returns a list
            CHANNEL_DETAILS         = "".join(CHANNEL.xpath(".//text()"))
            
            # Test for " - " in string
            if " - " in CHANNEL_DETAILS:
                # If present, populate CHANNEL_NAME and CHANNEL_DESCRIPTION
                CHANNEL_NAME        = CHANNEL_DETAILS.split(" - ",1)[0]
                CHANNEL_DESCRIPTION = CHANNEL_DETAILS.split(" - ",1)[1]
            else:
                # If not present, populate CHANNEL_DESCRIPTION with nothing
                CHANNEL_NAME        = CHANNEL_DETAILS
                CHANNEL_DESCRIPTION = "No Description is available for this channel"
                
            # Appends the channel details to the CHANNEL_LIST
            CHANNEL_LIST.append([CHANNEL_NAME,CHANNEL_DESCRIPTION])
            
        return CHANNEL_LIST
        

################################################################################
# Defines the channel details
################################################################################
def DefineChannelDetails(CHANNEL,QUALITY):
    # Defines channel details from returned channel data
    CHANNEL_QUALITY     = QUALITY
    CHANNEL_TITLE       = CHANNEL[0] + " " + CHANNEL_QUALITY.upper()
    CHANNEL_SUMMARY     = CHANNEL[1]
    CHANNEL_NUMBER      = CHANNEL[0].replace("Channel ","channel")
    CHANNEL_THUMB       = "icon-" + CHANNEL[0].replace("Channel ","channel-") + "-" + CHANNEL_QUALITY + ".png"
    
    # Build an array containing the above
    CHANNEL_DETAILS     = [CHANNEL_QUALITY,
                            CHANNEL_TITLE,
                            CHANNEL_SUMMARY,
                            CHANNEL_NUMBER,
                            CHANNEL_THUMB]
    
    return CHANNEL_DETAILS

################################################################################
# Return EpisodeObject for channel
################################################################################
def CreateChannelEpisodeObject(QUALITY,TITLE,SUMMARY,NUMBER,THUMB,INCLUDE_CONTAINER=False):
    # Check the CHANNEL_QUALITY and set URL_CHANNEL, HEIGHT and WIDTH 
    # accordingly. N.B. URL wont work unless constructed here (rather than 
    # within the MediaObject)
    if "sd" in QUALITY:
        VIDEO_FILE      = NUMBER + "-" + QUALITY + VIDEO_SUFFIX
        HEIGHT          = 360
        WIDTH           = 640
    else:
        VIDEO_FILE      = NUMBER + VIDEO_SUFFIX
        HEIGHT          = 720
        WIDTH           = 1280
    
    # Builds a correctly formatted URL for each stream using a random IP number
    # from the CHANNEL_IPS array
    VIDEO_URL           = "http://82.80.192.2/iba_channel-511MRepeat/_definst_/smil:channel-511M.smil/playlist.m3u8"
    
    # Creates a VideoClipObject, with the key being a callback, unsure why, but
    # this re-calling of the same function is necessary to get an object that
    # will play without a URL service.
    #
    # N.B. HTTPLiveStreamURL automatically sets video_codec, audio_codec and 
    # protocol. Adding them back in causes the stream not to work on other
    # devices that are not Chrome and PHT
    CHANNEL_OBJECT              = VideoClipObject(
        key                     = Callback(
            CreateChannelEpisodeObject,
            QUALITY             = QUALITY,
            TITLE               = TITLE,
            SUMMARY             = SUMMARY,
            NUMBER              = NUMBER,
            THUMB               = THUMB,
            INCLUDE_CONTAINER   = True
        ),
        rating_key              = NUMBER + QUALITY,
        title                   = TITLE,
        summary                 = SUMMARY,
        thumb                   = R(THUMB),
        items                   = [
            MediaObject(
                video_resolution        = HEIGHT,
                audio_channels          = 2,
                optimized_for_streaming = True,
                height                  = HEIGHT,
                width                   = WIDTH,
                parts                   =   [
                    PartObject(
                        key             = HTTPLiveStreamURL(
                            url         = VIDEO_URL   
                        )
                    )
                ]
            )
        ]
    )
    
    if INCLUDE_CONTAINER:
        return ObjectContainer(
            objects               = [CHANNEL_OBJECT]
        )
    else:
        return CHANNEL_OBJECT

################################################################################
# Build the main menu
################################################################################ 
@handler(PREFIX, TITLE, thumb = ICON, art = ART)

def MainMenu():
    # Check to see if the user is logged in or not, if they are build the main
    # menu options, if not try to authenticate or show an error
  #  if "Login" in Dict:
        # Open an ObjectContainer for the main menu
        MAIN_MENU               = ObjectContainer()        
        
        # Add the HD streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "HD Streams",
                thumb           = R("icon-live-streams-hd.png"),
                summary         = "High definition streams",
                key             = Callback(
                    HDStreams,
                    TITLE       = "HD Streams"
                )
            )
        )
        
        # Add the SD streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "SD Streams",
                thumb           = R("icon-live-streams-sd.png"),
                summary         = "Standard definition streams",
                key             = Callback(
                    SDStreams,
                    TITLE       = "SD Streams"
                )
            )
        )
        
        # Add the Upcoming streams object
        MAIN_MENU.add(
            DirectoryObject(
                title           = "Upcoming Streams",
                thumb           = R("icon-upcoming-streams.png"),
                summary         = "Streams for the next week",
                key             = Callback(
                    UpcomingStreams,
                    TITLE       = "Upcoming Streams"
                )
            )
        )
        
        # Add the preferences object
        MAIN_MENU.add(
            PrefsObject(
                title           = "Preferences",
                thumb           = R("icon-preferences.png"),
                summary         = "Enter your username and password\r\nThe plugin will not work without them"
            )
        )
        
        return MAIN_MENU
        
   # else:
        # Log the user in initially
   #     AUTHENTICATE            = AuthenticateUser()
        
    #    if AUTHENTICATE is True:
            # Return the main menu
            MENU                = MainMenu()
            
            return MENU
     #   else:
            # Incorrect username or password error
      #      ERROR_MESSAGE       = ErrorIncorrectLogin()
            
       #     return ERROR_MESSAGE

################################################################################
# HD Streams menu
################################################################################   
# Set the route for the live streams HD menu
@route(PREFIX + "/hd-streams")

def HDStreams(TITLE):
    # Open an ObjectContainer for the live streams HD menu
    HD_STREAMS_MENU         = ObjectContainer(
        title1              = TITLE
    )

    # Gets the channel list
    CHANNEL_LIST            = GetChannelList()
    
    # Loop through each channel to produce an EpisodeObject
    for CHANNEL in CHANNEL_LIST:
        # Get this channels details
        CHANNEL_DETAILS     = DefineChannelDetails(CHANNEL,"hd")
        
        # Creates an EpisodeObject and adds it to the HD Streams menu
        HD_STREAMS_MENU.add(
            CreateChannelEpisodeObject(
                QUALITY     = CHANNEL_DETAILS[0],
                TITLE       = CHANNEL_DETAILS[1],
                SUMMARY     = CHANNEL_DETAILS[2],
                NUMBER      = CHANNEL_DETAILS[3],
                THUMB       = CHANNEL_DETAILS[4]
            )
        )
        
    return HD_STREAMS_MENU
    
################################################################################
# SD Streams menu
################################################################################   
# Set the route for the live streams SD menu
@route(PREFIX + "/sd-streams")

def SDStreams(TITLE):
    # Open an ObjectContainer for the live streams SD menu
    SD_STREAMS_MENU         = ObjectContainer(
        title1              = TITLE
    )

    # Gets the channel list
    CHANNEL_LIST            = GetChannelList()
    
    # Loop through each channel to produce an Episode object
    for CHANNEL in CHANNEL_LIST:
        # Get this channels details
        CHANNEL_DETAILS     = DefineChannelDetails(CHANNEL,"sd")
        
        # Creates an EpisodeObject and adds it to the HD Streams menu
        SD_STREAMS_MENU.add(
            CreateChannelEpisodeObject(
                QUALITY     = CHANNEL_DETAILS[0],
                TITLE       = CHANNEL_DETAILS[1],
                SUMMARY     = CHANNEL_DETAILS[2],
                NUMBER      = CHANNEL_DETAILS[3],
                THUMB       = CHANNEL_DETAILS[4]
            )
        )
        
    return SD_STREAMS_MENU
