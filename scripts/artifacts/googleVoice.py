__artifacts_v2__ = {
    "googlevoice_accounts": {
        "name": "Google Voice - User Accounts",
        "description": "Parses Google Voice User Accounts",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-08-08",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (October 29th, 2025). Tested on Samsung and Motorola devices.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/AccountData.pb', '*/data/com.google.android.apps.googlevoice/files/accounts/*/SqliteKeyValueCache:VoiceAccountCache.db'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "function": "googlevoice_accounts",
    },
    "googlevoice_calls": {
        "name": "Google Voice - User Calls",
        "description": "Parses Google Voice Call History",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-08-20",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (October 29th, 2025). Tested on Samsung and Motorola devices.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db', '*/data/com.google.android.apps.googlevoice/cache/audio/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone",
        "function": "googlevoice_calls",
    },
    "googlevoice_voicemails": {
        "name": "Google Voice - Voicemails",
        "description": "Parses Google Voice Voicemails",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-09-03",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (October 29th, 2025). Tested on Samsung and Motorola devices.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db', '*/data/com.google.android.apps.googlevoice/cache/audio/*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "voicemail",
        "function": "googlevoice_voicemails",
    },
    "googlevoice_messages": {
        "name": "Google Voice - Messages",
        "description": "Parses Google Voice Messages",
        "author": "William Campbell (@campwill), Eli Ehresmann (@H-Seek), Reina Girouard (@rgrd59), Paula Rokusek (@paula-rokusek)",
        "creation_date": "2025-10-22",
        "last_update_date": "2025-10-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Voice",
        "notes": "Tested on version 2025.07.20.788599304 (October 29th, 2025). Tested on Samsung and Motorola devices.",
        "paths": ('*/data/com.google.android.apps.googlevoice/files/accounts/*/SqliteKeyValueCache:VoiceAccountCache.db', '*/data/com.google.android.apps.googlevoice/files/accounts/*/LegacyMsgDbInstance.db', '*/data/com.google.android.apps.googlevoice/cache/Photo MMS images/*', '*/data/com.samsung.android.providers.contacts/databases/contact*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "function": "googlevoice_messages",
    }
}

import blackboxprotobuf
import os
import time
import struct
import inspect
from scripts.ilapfuncs import artifact_processor, get_binary_file_content, open_sqlite_db_readonly, does_table_exist_in_db, check_in_media

@artifact_processor
def googlevoice_accounts(files_found, report_folder, seeker, wrap_text):
    data_headers = [
        ("Account Number", "text"), 
        ("Full Name", "text"), 
        ("Email Address", "text"),
        ("Linked Phone Number", "text"),
        ("Google Voice Number", "text"),]
    data_list = []
    source_path = ""

    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("VoiceAccountCache.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'AccountData.pb':
                source_path = file
                pb = get_binary_file_content(file)

                message = blackboxprotobuf.decode_message(pb)

                # check for data in the account
                if '2' in message[0]:
                    if len(accounts) == 1:
                        account_number = message[0]['2']['1']
                        full_name = message[0]['2']['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2']['2']['2']['3'].decode('utf-8')
                    elif len(accounts) > 1:
                        account_number = message[0]['2'][i]['1']
                        full_name = message[0]['2'][i]['2']['2']['2'].decode('utf-8')
                        email_address = message[0]['2'][i]['2']['2']['3'].decode('utf-8')
                else:
                    account_number = ""
                    full_name = ""
                    email_address = ""

            if os.path.basename(file).endswith("VoiceAccountCache.db"):
                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                if accounts[i] == int(parts[user_index]):
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    cursor.execute('''
                    SELECT
                    response_data
                    FROM
                    cache_table
                    ''')

                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                message = blackboxprotobuf.decode_message(pb)

                # check account data exists
                if '3' in message[0]:
                    if '2' in message[0]['3']:
                        linked_number = message[0]['3']['2']['1']['1'].decode('utf-8')
                    else:
                        linked_number = ""
                    if '1' in message[0]['3']:
                        voice_number = message[0]['3']['1']['1']['1'].decode('utf-8')
                    else:
                        voice_number = ""

        if account_number:
            data_list.append((account_number,full_name,email_address,linked_number,voice_number))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_calls(files_found, report_folder, seeker, wrap_text):
    data_headers = [
        ("Account Number", "text"), 
        ("Timestamp", "text"), 
        ("Direction", "text"),
        ("Caller", "text"),
        ("Recipient", "text"),
        ("Call Status", "text"),
        ("Voicemail Left", "text"),
        ("Duration", "text"),
        ("Read Status", "text"),
        ("Audio Recording", "media")]
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("LegacyMsgDbInstance.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    # get the call data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                # get the path of the first account's db
                if source_path_found == False:
                    source_path = file
                    source_path_found = True

                if accounts[i] == int(parts[user_index]):
                    account_number = accounts[i]
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    if does_table_exist_in_db(file, 'message_t'):
                        cursor.execute('''
                        SELECT
                        message_blob
                        FROM
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                        message = blackboxprotobuf.decode_message(pb)

                        # check if the entry is a call (answered, missed, outgoing)
                        # 13 = 1 for an answered call
                        # 13 = 2 for an outgoing call
                        # 22 has a value if a call was missed or declined
                        if message[0]['13'] == 1 or message[0]['13'] == 2 or ('22' in message[0]):

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            if message[0]['13'] == 1 or ('22' in message[0]):
                                direction = "Incoming"
                                from_num = str(message[0]['4']['1'].decode('utf-8'))
                                to_num = message[0]['3'].decode('utf-8') # GV number

                            elif message[0]['13'] == 2:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number
                                to_num = message[0]['4']['1'].decode('utf-8')

                            # Call Status
                            call_status = ""
                            if '22' in message[0]:
                                call_status = "Missed"
                            elif message[0]['13'] == 1:
                                call_status = "Answered"

                            # Voicemail
                            # 13 = 3 if a voicemail was left
                            if message[0]['13'] == 3:
                                voicemail = "Yes"
                            else:
                                voicemail = "No"

                            # Duration
                            duration = message[0]['9']
                            duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                            duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Recording
                            # 23 has values if an incoming call was recorded
                            recording = ""
                            if '23' in message[0]:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')
                                recording = ""

                                # get the audio file
                                for audio_file in files_found:
                                    if "audio" in audio_file and message_id in audio_file:
                                        recording = check_in_media(artifact_info, report_folder, seeker, files_found, audio_file)
                                        break
                                
                                data_list.append((account_number,timestamp,direction,from_num,to_num,call_status,voicemail,duration,read_status,recording))

                            else:
                                data_list.append((account_number,timestamp,direction,from_num,to_num,call_status,voicemail,duration,read_status,recording))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_voicemails(files_found, report_folder, seeker, wrap_text):
    data_headers = [
        ("Account Number", "text"), 
        ("Timestamp", "text"), 
        ("Caller", "text"),
        ("Recipient", "text"),
        ("Duration", "text"),
        ("Read Status", "text"),
        ("Transcript", "text"),
        ("Audio File", "media")]
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("LegacyMsgDbInstance.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    # get the voicemail data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                # get the path of the first account's db
                if source_path_found == False:
                    source_path = file
                    source_path_found = True

                if accounts[i] == int(parts[user_index]):
                    account_number = accounts[i]
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    if does_table_exist_in_db(file, 'message_t'):
                        cursor.execute('''
                        SELECT
                        message_blob
                        FROM
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        pb = row[0]
                        message = blackboxprotobuf.decode_message(pb)

                        # check if the entry is a voicemail
                        # 13 = 3 for a voicemail is received
                        if message[0]['13'] == 3:

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Caller
                            from_num = str(message[0]['4']['1'].decode('utf-8'))

                            # Recipient
                            to_num = message[0]['3'].decode('utf-8') # GV number

                            # Duration
                            duration = message[0]['9']
                            duration = struct.unpack('f', struct.pack('I', duration))[0] # convert int32 value to a float
                            duration = time.strftime("%H:%M:%S", time.gmtime(duration)) # convert seconds to Hours:Minutes:Seconds

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Transcript
                            # 7[2] holds the transcript of the voicemail broken into word and special character segments
                            if '7' in message[0]:
                                transcript = ""
                                num_words = len(message[0]['7']['2'])
                                for j in range(num_words):
                                    word = message[0]['7']['2'][j]['1'].decode('utf-8')
                                    if word != "":
                                        transcript += word + " "
                            else:
                                transcript = "Transcript Not Available"

                            # Audio File
                            artifact_info = inspect.stack()[0]
                            message_id = message[0]['1'].decode('utf-8')
                            audio = ""
                            # get the voicemail audio file
                            for audio_file in files_found:
                                if "audio" in audio_file and message_id in audio_file:
                                    audio = check_in_media(artifact_info, report_folder, seeker, files_found, audio_file)
                                    break

                            if timestamp:
                                data_list.append((account_number,timestamp,from_num,to_num,duration,read_status,transcript,audio))

    return data_headers, data_list, source_path

@artifact_processor
def googlevoice_messages(files_found, report_folder, seeker, wrap_text):
    data_headers = [
        ("Account Number", "text"), 
        ("Timestamp", "text"), 
        ("Conversation ID", "text"),
        ("Direction", "text"),
        ("Sender", "text"),
        ("Recipient(s)", "text"),
        ("Read Status", "text"),
        ("Message", "text"),
        ("Image", "media")]
    data_list = []
    source_path = ""

    # get a list of accounts
    accounts = []
    for file in files_found:
        if os.path.basename(file).endswith("VoiceAccountCache.db"):
            parts = file.split(os.sep)
            user_index = parts.index("accounts") + 1
            accounts.append(int(parts[user_index]))

    # get the message data
    source_path_found = False
    for i in range(len(accounts)):
        for file in files_found:
            if os.path.basename(file) == 'LegacyMsgDbInstance.db':

                parts = file.split(os.sep)
                user_index = parts.index("accounts") + 1

                # get the path of the first account's db
                if source_path_found == False:
                    source_path = file
                    source_path_found = True

                if accounts[i] == int(parts[user_index]):
                    account_number = accounts[i]
                    db = open_sqlite_db_readonly(file)
                    cursor = db.cursor()
                    if does_table_exist_in_db(file, 'message_t'):
                        cursor.execute('''
                        SELECT
                        message_blob,
                        conversation_id
                        FROM
                        message_t
                        ''')
                all_rows = cursor.fetchall()
                usageentries = len(all_rows)
                if usageentries > 0:
                    for row in all_rows:
                        # conversation_id starts with "t" for individual messages
                        if row[1].startswith("t"):
                            pb = row[0]
                            message = blackboxprotobuf.decode_message(pb)

                            # Conversation ID
                            conversation_id = row[1]

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            # 13 = 5 when a message is received
                            # 13 = 6 when a message is sent
                            if message[0]['13'] == 5:
                                direction = "Incoming"
                                from_num = message[0]['4']['1'].decode('utf-8')
                                to_nums = message[0]['3'].decode('utf-8') # GV number
                            elif message[0]['13'] == 6:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number
                                to_nums = message[0]['4']['1'].decode('utf-8')

                            # Message
                            message_content = message[0]['10'].decode('utf-8')

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Image
                            if "MMS" in message_content:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')

                                # get image file
                                for image in files_found:
                                    # image file resides in Photo MMS images folder
                                    # filename: message_id + "-14" + extension
                                    if "Photo MMS images" in image and message_id in image and "-14" in image:
                                        thumb = check_in_media(artifact_info, report_folder, seeker, files_found, image)
                                        data_list.append((account_number,timestamp,conversation_id,direction,from_num,to_nums,read_status,message_content,thumb))
                                        break

                            else:
                                data_list.append((account_number,timestamp,conversation_id,direction,from_num,to_nums,read_status,message_content,""))

                        # conversation_id starts with "g" for group chat messages
                        elif row[1].startswith("g"):
                            pb = row[0]
                            message = blackboxprotobuf.decode_message(pb)

                            # Conversation ID
                            conversation_id = row[1]

                            # Timestamp
                            timestamp = message[0]['2'] / 1000 # convert to seconds
                            timestamp = time.strftime('%Y/%m/%d %H:%M:%S', time.gmtime(timestamp)) # convert to UTC time

                            # Direction
                            # 5 exists in 15 when the message is received
                            if '5' in message[0]['15']:
                                direction = "Incoming"
                                from_num = message[0]['15']['5'].decode('utf-8')

                                to_nums_list = [] # GV number & other group chat members
                                to_nums_list.append(message[0]['3'].decode('utf-8')) # GV number
                                for i in range(len(message[0]['15']['4'])):
                                    if message[0]['15']['4'][i]['1'].decode('utf-8') != from_num:
                                        to_nums_list.append(message[0]['15']['4'][i]['1'].decode('utf-8'))

                            # 5 does not exist in 15 when the message is sent
                            elif '5' not in message[0]['15']:
                                direction = "Outgoing"
                                from_num = message[0]['3'].decode('utf-8') # GV number

                                to_nums_list = [] # other group chat members
                                for i in range(len(message[0]['15']['4'])):
                                    to_nums_list.append(message[0]['15']['4'][i]['1'].decode('utf-8'))

                            to_nums = ', '.join(to_nums_list)

                            # Message
                            message_content = message[0]['15']['1'].decode('utf-8')

                            # Read Status
                            if message[0]['6'] == 0:
                                read_status = "Unread"
                            elif message[0]['6'] == 1:
                                read_status = "Read"

                            # Image
                            if "MMS" in message_content:
                                artifact_info = inspect.stack()[0]
                                message_id = message[0]['1'].decode('utf-8')

                                # get the image file
                                for image in files_found:
                                    # image file resides in Photo MMS images folder
                                    # filename: message_id + "-14" + extension
                                    if "Photo MMS images" in image and message_id in image and "-14" in image:
                                        thumb = check_in_media(artifact_info, report_folder, seeker, files_found, image)
                                        data_list.append((account_number,timestamp,conversation_id,direction,from_num,to_nums,read_status,message_content,thumb))
                                        break

                            else:
                                data_list.append((account_number,timestamp,conversation_id,direction,from_num,to_nums,read_status,message_content,""))

    return data_headers, data_list, source_path
