import psycopg2
from transformers import pipeline
import pandas as pd
import requests
from transformers import pipeline
import pandas as pd
from lingua import Language, LanguageDetectorBuilder
import warnings
warnings.filterwarnings("ignore")

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="PPG",
        user="great",
        password="8120857"
    )
    return conn

def get_accounts_data():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM accounts")
        rows = cur.fetchall()
        accounts_data = [dict(zip(['id', 'username', 'password', 'name', 'email', 'address', 'userrole'], row)) for row in rows]
        return accounts_data
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error fetching data:", error)
    finally:
        cur.close()
        conn.close()

def get_orders_data():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall()
        orders_data = [dict(zip(['id', 'user_id', 'timestamp', 'order_details', 'status', 'type','percent'], row)) for row in rows]
        return orders_data
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error fetching data:", error)
    finally:
        cur.close()
        conn.close()

def save_order_to_postgres(user_id,order_details, status, types,percent):  
    sql = 'INSERT INTO orders (user_id, order_details, status, type, percent) VALUES (%s, %s, %s, %s, %s)'
    values = (user_id, order_details, status, types, percent)
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, values)
            conn.commit()
            print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error inserting data:", error)

def update_order_to_postgres(order_id, status):  
    sql = "UPDATE orders SET status = %s WHERE id = %s"
    values = (status, order_id)
    try:
        with get_connection() as conn, conn.cursor() as cur:
            cur.execute(sql, values)
            conn.commit()
            print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error inserting data:", error)

def regis_data_to_postgres(username, password, fullname, email, address):
    conn = get_connection()
    cur = conn.cursor()   
    sql = "INSERT INTO accounts (username, password, name, email, address, userrole) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, password, fullname, email, address, 'customer')
    try:
        cur.execute(sql, values)
        conn.commit()
        print("Data inserted successfully")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error inserting data:", error)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

#def zeroshot_classification(order_details):
#    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
#    sequence_to_classify = order_details   
#    candidate_labels = ['waterworks','electrical','structural','arborist','pesticide']

#    output = classifier(sequence_to_classify, candidate_labels)   
#    df = pd.DataFrame({
#        "type":output['labels'],
#        "scores":output['scores']
#    })

#    dfsort = df.sort_values(by='scores', ascending=False)    
#    top_result = dfsort.iloc[0].to_dict()  

#    return top_result

def active_send_line(user_role,details):   
    if user_role == 'waterworks':
        token ='NkoNW7CaPCurL3cMssBAgYLUwjKTFq9YREuRBdGHOOV' #pat
    if user_role == 'electrical':
        token = 'bBduCFbG8vhwvb4fqOMqnvRoykYXrn1UmVfjZoTSBTA' #pun   
    
    #token = 'zF9iq9nrmtSXoi0Nr3DFucH0M2uf4uvUy0f7ddiYP8Q'
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded', 'Authorization' : 'Bearer '+token}
    session = requests.Session()    
    img_url = 'https://t4.ftcdn.net/jpg/04/64/26/33/240_F_464263387_P5CimoOiH5MFD5vv6WCyUBoLOGdQd82z.jpg'
    data = {'message': f'Work destails : {details} ','imageThumbnail': img_url, 'imageFullsize': img_url}

    return session.post(url, headers=headers, data=data)


def translator(order_details):    
    languages = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH]
    detector = LanguageDetectorBuilder.from_languages(*languages).build()
    language = detector.detect_language_of(order_details)

    if language == Language.ENGLISH:
        en_text = order_details
    else:
        if language == Language.SPANISH:
            esp_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
            en_text = esp_pipe(order_details)[0]['translation_text']
        elif language == Language.FRENCH:
            fr_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
            en_text = fr_pipe(order_details)[0]['translation_text']
        elif language == Language.GERMAN:
            gm_pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-de-en")
            en_text = gm_pipe(order_details)[0]['translation_text']

    # Initialize the zero-shot classification pipeline
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    sequence_to_classify = en_text

    candidate_labels = ['waterworks','electrical','structural','arborist','pesticide']

    output = classifier(sequence_to_classify, candidate_labels)

    df1 = pd.DataFrame({
        "type": output['labels'],
        "scores": output['scores']
    })

    dfsort = df1.sort_values(by='scores', ascending=False)
    top_result = dfsort.iloc[0].to_dict()  

    return top_result
