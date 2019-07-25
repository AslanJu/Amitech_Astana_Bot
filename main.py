import flask
appname="amitech-astana-bot"

server = flask.Flask(__name__)

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telebot
from telebot import types

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('ServiceAccount.json', scope)
gs = gspread.authorize(creds)

xl = gs.open("Test")
sheet = xl.worksheet("Sheet1")

token="808993087:AAE360M4S1wUapWVWFxRAnwqDp2-g1D2h20"
bot=telebot.TeleBot(token)

DN=""
PN=""
SN=""
L=""

@bot.message_handler(commands=['start'])
def handle_command(msg):
    name=msg.chat.first_name
    bot.send_message(msg.chat.id,"Здравствуйте, "+name+"!")
    bot.send_message(msg.chat.id,'Я, Бот-прайс-лист ТОО "Amitech Astana" (Амитех Астана).')
    bot.send_message(msg.chat.id,'Буду рад помочь Вам с поиском цен на наши трубы!')
    ans=bot.send_message(msg.chat.id,"Пожалуйста, укажите диаметр труб от 300 до 3000 (мм)")
    bot.register_next_step_handler(ans, check_diameter)

def check_diameter(msg):
    global DN
    if msg.text.isdigit():
        if 3000>=int(msg.text)>=300:
            DN=msg.text
            ans=bot.send_message(msg.chat.id,"Пожалуйста, укажите класс давления труб от 1 до 16 (атм)")
            bot.register_next_step_handler(ans, check_pressure)
        else:
            ans=bot.send_message(msg.chat.id,"Пожалуйста, проверьте верность введенного диаметра")
            bot.register_next_step_handler(ans, check_diameter)
    else:
        ans=bot.send_message(msg.chat.id,"Ошибка! Пожалуйста, введите численное значение")
        bot.register_next_step_handler(ans, check_diameter)

def check_pressure(msg):
    global PN
    if msg.text.isdigit():
        if 16>=int(msg.text)>=1:
            PN=msg.text
            ans=bot.send_message(msg.chat.id,"Пожалуйста, укажите класс жёсткости 5000 или 10000 (Н/м)")
            bot.register_next_step_handler(ans, check_stiffness)
        else:
            ans=bot.send_message(msg.chat.id,"Пожалуйста, проверьте верность введенного класса давления (должен быть 1, 6, 10 или 16 (атм))")
            bot.register_next_step_handler(ans, check_pressure)
    else:
        ans=bot.send_message(msg.chat.id,"Ошибка! Пожалуйста, введите численное значение")
        bot.register_next_step_handler(ans, check_pressure)
         
def check_stiffness(msg):
    global SN
    if msg.text.isdigit():
        if int(msg.text)==5000 or int(msg.text)==10000:
            SN=msg.text
            ans=bot.send_message(msg.chat.id,"Пожалуйста, укажите длину трубы 6 или 12 (п.м.)")
            bot.register_next_step_handler(ans, check_lenght)
        else:
            ans=bot.send_message(msg.chat.id,"Пожалуйста, проверьте верность введенного класса жёсткости (должен быть 5000 или 10000 (Н/м))")
            bot.register_next_step_handler(ans, check_stiffness)
    else:
        ans=bot.send_message(msg.chat.id,"Ошибка! Пожалуйста, введите численное значение")
        bot.register_next_step_handler(ans, check_stiffness)
def check_lenght(msg):
    global L
    if msg.text.isdigit():
        if int(msg.text)==6 or int(msg.text)==12:
            L=msg.text
            bot.send_message(msg.chat.id,"Пожалуйста, подождите. Ваш запрос обрабатывается ...")
            show_result(msg)
        else:
            ans=bot.send_message(msg.chat.id,"Пожалуйста, проверьте длину трубы (длина должна быть 6 или 12 (м)")
            bot.register_next_step_handler(ans, check_lenght)
    else:
        ans=bot.send_message(msg.chat.id,"Ошибка! Пожалуйста, введите численное значение")
        bot.register_next_step_handler(ans, check_lenght)


def show_result(msg):
    global DN
    global PN
    global SN
    global L

    
    DN_List=sheet.findall(DN)
    PN_List=[]
    for c in DN_List:
        if sheet.cell(c.row, 2).value==PN:
            PN_List.append(sheet.cell(c.row, 2))
        SN_List=[]
    for c in PN_List:
        if sheet.cell(c.row, 3).value==SN:
            SN_List.append(sheet.cell(c.row, 3))
    
    result=""
    for c in SN_List:
        if sheet.cell(c.row, 4).value==L:
            result = sheet.cell(c.row, 5)
    if result=="":
        bot.send_message(msg.chat.id,'Заданной Вами номенклатуры не существует в базе. По вопросам цен на такую продукцию, просим Вас обратиться в ТОО "Amitech Astana" (Амитех Астана):/n № телефона +7 /7172/ 67 76 76')
    else:
        bot.send_message(msg.chat.id,"Цена, выбранной Вами трубы, DN"+DN+"-PN"+PN+"-SN"+SN+"-L="+L+"м. = "+str((result.value))+" тенге за п.м. трубы")


@server.route('/' + token, methods=['POST'])
def get_message():
bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
return "!", 200

@server.route('/', methods=["GET"])
def index():
bot.remove_webhook()
bot.set_webhook(url=f"https://{appname}.herokuapp.com/{token}")
return "Hello from Heroku!", 200


if __name__ == "__main__":
server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


