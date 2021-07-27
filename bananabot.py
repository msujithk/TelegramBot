from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import requests
import re
import logging
import os
import glob
import json
import time
from os import path
bananabot  = None
PRICE = 0
BOUNCE_PRICE = 1
REJECTION_PRICE = 2
STOP_LOSS = 3
FINAL_PRICE = 4

class State:
    def __int__(self):
        self.input = None
        self.mode = None
        self.currency = None

class BananaBot:
    def __init__(self):
        root = os.path.dirname(os.path.abspath(__file__))
        root_dir = root.split('/')
        self.root_path = '/' +  root_dir[1] + '/' + root_dir[2]
        self.order_book = {'buy':[], 'sell':[]}
        self.state = {}
        self.read_book()
        self.bot = None
        '''
        self.key_board_button = []
        root = os.path.dirname(os.path.abspath(__file__))
        print (root)
        root_dir = root.split('/')
        self.root_path = '/' +  root_dir[1] + '/' + root_dir[2]
        print (self.root_path)
        for root, dirs, files in os.walk(self.root_path, topdown = True):
            for directory in dirs:
                path =  self.root_path + '/' + directory
                if len(path) > 0:
                    for filename in os.listdir(path):
                        if filename.endswith(".json"):
                            if re.match(r".*positions.json", filename):
                                self.key_board_button.append( InlineKeyboardButton(text=directory, callback_data = directory))
                                break
            break
        '''

    def buy_wbi(self, user_name,update, context):
        #context.bot.send_message(chat_id=update.effective_chat.id, text= f'Buy WBI with?')        
        reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton(text='EOS', callback_data = 'eos'+':'+user_name)],[InlineKeyboardButton(text='USD', callback_data = 'usd'+':'+user_name)]], one_time_keyboard = True)
        context.bot.send_message(chat_id=update.effective_chat.id,text="Buy WBI with?", reply_markup=reply_markup)
   

    def sell_wbi(self, user_name,update, context):
        #context.bot.send_message(chat_id=update.effective_chat.id, text= f'Sell WBI for?')
        reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton(text='EOS', callback_data = 'eos'+':'+user_name)],[InlineKeyboardButton(text='USD', callback_data = 'usd'+':'+user_name)]],one_time_keyboard = True)
        context.bot.send_message(chat_id=update.effective_chat.id,text="Sell WBI for?", reply_markup=reply_markup)


    def button(self,update, context):
        pass
        # if data ==  'buy':
        #     self.buy_wbi(user_name)
        #     self.state[user_name].mode = 'buy'
        # elif data ==  'sell':
        #     self.sell_wbi(user_name)
        #     self.state[user_name].mode = 'sell'
        # elif data == 'bids':
        #     self.state[user_name].mode = 'SEEBID'
        #     self.view_bid(user_name)
        # elif data == 'eos':
        #     context.bot.send_message(chat_id=update.effective_chat.id, text= f'Enter {self.state[user_name].mode} price in EOS') #self.state[user_name].message =
        #     self.state[user_name].currency = 'EOS'
        # elif data == 'usd':
        #     context.bot.send_message(chat_id=update.effective_chat.id, text= f'Enter {self.state[user_name].mode} price in USD') #self.state[user_name].message =
        #     self.state[user_name].currency = 'USD'
        # elif data == 'remove':
        #     self.remove_order(user_name)



    def save_book(self, data_dict):
        #data_dict["Long_positions"] = long_dict_array
        #data_dict["Short_positions"] = short_dict_array
        json_path = path =  self.root_path + '/' + 'OTC_BOOK.json'
        with open(json_path, 'w') as fp:
            json.dump(data_dict, fp)



    def read_book(self):
        pth = self.root_path + '/' + 'OTC_BOOK.json'
        if path.exists(pth) is False:
            return
        try:
            with open(pth) as f:
                self.order_book = json.load(f)
        except Exception as e:
            print('Exception occured during read' + str(e))
    


    def start(self,update, context):
        print (update.message)
        self.type = update.message.chat['type']
        user = update.message.from_user
        user_name  = user['username']
        print(user_name)
        if user_name == None:
            print (update.message.from_user['first_name'])
            user_name = update.message.from_user['first_name']
        if user_name in self.state:
            pass
        else:
            self.state[user_name] = State()

        if self.type == 'private':
            context.bot.send_message(chat_id=update.effective_chat.id,text=f'Hello {user_name}, Welcome to Chester Cool\'s WBI OTC solutions')
            reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton(text='Buy WBI', callback_data = 'buy' +':'+user_name )],[InlineKeyboardButton(text='Sell WBI', callback_data = 'sell' +':'+user_name )],[InlineKeyboardButton(text='View Order Book', callback_data = 'bids' + ':'+user_name )]], one_time_keyboard = True)
            context.bot.send_message(chat_id=update.effective_chat.id,text="Select one", reply_markup=reply_markup)
        else:
            self.view_bid(user_name, update, context)


    def text_entered(self,update, context):
        if self.type != 'private':
            return
        print(update.message)
        user_name = update.message.from_user['username']
        if user_name == None:
            print(update.message.from_user['first_name'])
            user_name = update.message.from_user['first_name']
        if user_name in self.state:
            pass
        else:
            self.state[user_name] = State()
        self.type = update.message.chat['type']
        text = update.message.text#.lower()
        if re.match(r".*price.*",text):
            self.price_entered( text, user_name, update, context)
        elif re.match(r".*quantity.*",text):
            self.quantity_entered(text,user_name,update, context)

        elif re.match(r".*Your orders.*",text):
            self.remove_entered( text, user_name, update, context)
        elif text == 'Buy WBI':
            self.buy_wbi(user_name,update, context)
            self.state[user_name].mode = 'buy'
        elif text == 'Sell WBI':
            self.sell_wbi(user_name, update, context)
            self.state[user_name].mode = 'sell'
        elif text == 'View Order Book':
            self.state[user_name].mode = 'SEEBID'
            self.view_bid(user_name, update, context)
        elif text == 'Remove Order':
            self.state[user_name].input = 'Remove'
            self.remove_order(user_name, update, context)
        elif text == 'EOS':
            self.state[user_name].input = 'price'
            context.bot.send_message(chat_id=update.effective_chat.id, text= f'Enter {self.state[user_name].mode} price in EOS')
            self.state[user_name].currency = 'EOS'
        elif text == 'USD':
            self.state[user_name].input = 'price'
            context.bot.send_message(chat_id=update.effective_chat.id, text= f'Enter {self.state[user_name].mode} price in USD')
            self.state[user_name].currency = 'USD'
        elif text == 'Cancel Remove Order':
            self.state[user_name].input = ''
            self.start(update, context)
        else:
            if self.state[user_name].input == 'quantity':
                self.quantity_entered(text, user_name, update, context)
            elif self.state[user_name].input == 'price':
                self.state[user_name].input = 'quantity'
                self.price_entered(text, user_name, update, context)
            elif self.state[user_name].input == 'Remove':
                self.remove_entered(text, user_name, update, context)
                self.state[user_name].input = ''
            else:
                if self.type == 'private':
                    self.state[user_name].input = ''
                    self.start(update, context)



    def remove_entered(self,text, user_name, update, context):
        if self.is_number(text) is False:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f' Only numbers allowed, dont enter alphabets, ex: 20K = wrong 20000 = right \n Enter again')
            return
        if int(text) < 0:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Entered order number is incorrect, please have a look at the list again \n Enter order number again')
            return
        bid_side = self.order_book['buy']
        ask_side = self.order_book['sell']

        for bids in bid_side:
            for buyer, order in bids.items():
                if buyer == user_name:
                    if int(text) <= len(order):
                        order.pop(int(text) - 1)
                        break
                    else:
                        for bids_ask in ask_side:
                            for buyer, order_ask in bids_ask.items():
                                if (int(text) - len(order)) <= len(order_ask):
                                    order_ask.pop((int(text) - len(order)) - 1)
                                    break
                                else:
                                    context.bot.send_message(chat_id=update.effective_chat.id,
                                                             text=f'Entered order number is incorrect, please have a look at the list again \n Enter order number again')
                                    return

        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Order Removed Successfully')
        print(self.order_book)
        self.save_book(self.order_book)
        self.view_bid(user_name, update, context)


    def price_entered(self,text, user_name, update, context):
        if self.is_number(text) is False:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f' Only numbers allowed, dont enter alphabets, ex: 20K = wrong 20000 = right \n Enter again')
            return
        # if self.mode == 'BUY' or self.mode == 'SELL':
        self.price = text
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Enter WBI quantity to {self.state[user_name].mode}')


    def quantity_entered(self,text,user_name,update, context):
        if self.is_number(text) is False:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f' Only numbers allowed, dont enter alphabets, ex: 20K = wrong 20000 = right \n Enter again')
            return
        self.quantity = text
        user_exists = False

        print(self.order_book[self.state[user_name].mode])
        index = 0
        for item in self.order_book[self.state[user_name].mode]:
            if user_name in item:
                user_exists = True
                break
            index += 1

        if user_exists is True:
            print('USER EXISTS')
            ord_dict = {'name': update.message.from_user['first_name'],
                        'quantity': self.quantity, 'price': self.price,
                        'currency': self.state[user_name].currency}
            self.order_book[self.state[user_name].mode][index][user_name].append(ord_dict)

        else:
            ord_dict = {user_name: [{'name': update.message.from_user['first_name'],
                                     'quantity': self.quantity, 'price': self.price,
                                     'currency': self.state[user_name].currency}]}
            self.order_book[self.state[user_name].mode].append(ord_dict)
        self.save_book(self.order_book)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Order successfully added.')
        self.view_bid(user_name, update, context)

    def remove_order(self, user_name, update, context):
        bid_side = self.order_book['buy']
        ask_side = self.order_book['sell']
        self.remove_order_list = []
        bid_order_len = 0
        ask_order_len = 0
        count = 0
        text = 'Your orders \n'
        for bids in bid_side:
            for buyer, order in  bids.items():
                if buyer == user_name:
                    bid_order_len = len(order)
                    if len(order) > 0:
                        for ord in order:
                            count += 1
                            text += f'Order No:{count} ' + f'{ord}' + '\n' + '\n'
                    break
        for bids in ask_side:
            for seller, order in  bids.items():
                if seller == user_name:
                    ask_order_len = len(order)
                    if len(order) > 0:
                        for ord in order:
                            count += 1
                            text += f'Order No:{count} ' + f'{ord}' + '\n' + '\n'
                    break
        if (bid_order_len + ask_order_len) == 1:
            if bid_order_len == 1:
                for bids in bid_side:
                    for buyer, order in bids.items():
                        if buyer == user_name:
                            order.clear()
                            context.bot.send_message(chat_id=update.effective_chat.id,text=f'Order Removed Successfully')
                            self.save_book(self.order_book)
                            self.view_bid(user_name, update, context)
            elif ask_order_len == 1:
                for bids in ask_side:
                    for buyer, order in bids.items():
                        if buyer == user_name:
                            order.clear()
                            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Order Removed Successfully')
                            self.save_book(self.order_book)
                            self.view_bid(user_name, update, context)

        else:
            if (bid_order_len + ask_order_len) == 0:
                context.bot.send_message(chat_id=update.effective_chat.id, text="You dont have any orders")
            else:
                text += 'See the above list and enter the order number that you wish to delete. Ex enter 1 to remove Order No 1 (you can delete only 1 order at a time)'
                context.bot.send_message(chat_id=update.effective_chat.id, text= text)
                reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton(text='Cancel Remove Order', callback_data='Cancel Remove Order' + ':' + user_name)]],one_time_keyboard=True)
                context.bot.send_message(chat_id=update.effective_chat.id, text="Click to cancel remove order",
        reply_markup=reply_markup)
                 

    def view_order_book(self,update, context):
        self.bot = context.bot
        self.update = update
        user_name =  update.message.from_user['username']
        self.view_bid(user_name, update, context)

    def view_bid(self, user_name,update, context):
            user_order_present = False
            bid_side = self.order_book['buy']
            text = '=======< Bid Side>======' + '\n'
            #print(f'bid = {bid_side}')
            for bids in bid_side:
                for buyer, order in  bids.items():
                    if buyer == user_name and len(order) != 0:
                        user_order_present = True
                    #print (f'order = {order}')
                    for item in order:
                        name = item['name']
                        quantity = item['quantity']
                        price = item['price']
                        currency = item['currency']
                        if buyer == name:
                            usr_name = buyer
                        else:
                            usr_name = '@'+buyer

                        text += 'Buyer: '+name+'['+ usr_name +']'+ ' Quantity: '+ quantity + ' Price: ' + price + currency + '\n'
                        #print (text)
            #context.bot.send_message(chat_id=update.effective_chat.id, text= text)
            #self.bot.send_message(chat_id=self.update.effective_chat.id, text= f'=======< Ask Side>=====')
            ask_side = self.order_book['sell']
            text += '\n=======< Ask Side>=====' + '\n'
            #print(f'bid = {ask_side}')
            for bids in ask_side:
                for seller, order in  bids.items():
                    #print(f'order = {order}')
                    if seller == user_name  and len(order) != 0:
                        user_order_present = True
                    for item in order:
                        name=item['name']
                        quantity= item['quantity']
                        price = item['price']
                        currency = item['currency']
                        if seller == name:
                            usr_name = seller
                        else:
                            usr_name = '@'+seller
                        text +='Seller: '+name+'['+ usr_name +']'+' Quantity: '+ quantity + ' Price: '+price+currency + '\n'

            if self.type == 'private':
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)
                if user_order_present is True:
                    reply_markup = ReplyKeyboardMarkup([[InlineKeyboardButton(text='Remove Order', callback_data = 'remove' + ':'+user_name )]], one_time_keyboard = True)
                    context.bot.send_message(chat_id=update.effective_chat.id,text="Click if you want to remove order", reply_markup=reply_markup)
            else:
                text += '\n DM @WBI_OTC_BOT to Add or Remove orders'
                context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def is_number(self,num):
        try:
            float(num)   
        except ValueError:
            return False
        return True
        

def main():
    print('starting ....')
    global bananabot 
    bananabot = BananaBot()
    bananabot.bot = Updater(token = '', use_context=True)
    dp = bananabot.bot.dispatcher
    dp.add_handler(CommandHandler('otc',bananabot.start))
    dp.add_handler(CommandHandler('start', bananabot.start))
    #dp.add_handler(CommandHandler('v',bananabot.start))
    dp.add_handler(CallbackQueryHandler(bananabot.button))
    dp.add_handler(MessageHandler(Filters.text,bananabot.text_entered))
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    bananabot.bot.start_polling()
    bananabot.bot.idle()



if __name__ == '__main__':
    main()
