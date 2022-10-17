import random
import sqlite3


class SimpleBankingSystem:
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS card (
                id INTEGER NOT NULL PRIMARY KEY,
                number TEXT UNIQUE,
                pin TEXT,
                balance INTEGER DEFAULT 0);''')
    conn.commit()

    def main(self):
        while True:
            print(
                '''\n1. Create an account\n2. Log into account\n0. Exit''')
            choice = int(input())
            if choice == 1:
                self.create_account()
            elif choice == 2:
                self.logging()
            elif choice == 0:
                print('Bye!')
                self.cur.close(), self.conn.close()
                exit()

    def create_account(self):
        card_front = '400000'
        card_end = ""
        for _ in range(9):
            card_end += str(random.randrange(10))
        card_number = self.luhn_algorithm(card_front + card_end)
        card_pin = ""
        for _ in range(4):
            card_pin += str(random.randrange(10))
        print(f'''Your card number:\n{card_number}\nYour card PIN:\n{card_pin}''')
        self.cur.execute('''INSERT INTO card (number, pin)
                    VALUES (?, ?);''', (card_number, card_pin))
        self.conn.commit()

    def luhn_algorithm(self, card_number) -> str:
        card_number = [int(number) for number in card_number]
        luhn_check = 0
        for number in range(len(card_number)):
            new_number = card_number[number] * 2 if number % 2 == 0 else card_number[number]
            luhn_check += new_number if new_number <= 9 else new_number - 9
        last_number = 0 if luhn_check % 10 == 0 else 10 - (luhn_check % 10)
        return "".join([str(number) for number in card_number]) + str(last_number)

    def logging(self):
        print('\nEnter your card number:')
        card_number = input()
        print('Enter your PIN:')
        card_pin = input()
        print('')
        try:
            self.cur.execute('''SELECT pin FROM card WHERE number = ?;''', (card_number,))
            if self.cur.fetchone()[0] == card_pin:
                print('You have successfully logged in!')
                self.account_actions(card_number)
            else:
                print('Wrong card number or PIN!')
        except TypeError:
            print('Wrong card number or PIN!')

    def account_actions(self, card_number):
        while True:
            print('''\n1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit''')
            choice = int(input())
            if choice == 1:
                self.cur.execute('''SELECT balance FROM card WHERE number = ?''', (card_number,))
                print(f'Balance: {self.cur.fetchone()[0]}')
            elif choice == 2:
                print('Enter income:')
                self.cur.execute('''UPDATE card SET balance = balance + ? WHERE number = ?;''', (int(input()), card_number))
                self.conn.commit()
                print('Income was added!')
            elif choice == 3:
                self.transfer_money(card_number)
            elif choice == 4:
                self.cur.execute('''DELETE FROM card WHERE number = ?;''', (card_number,))
                self.conn.commit()
            elif choice == 5:
                break
            elif choice == 0:
                print('Bye!')
                self.cur.close(), self.conn.close()
                exit()

    def transfer_money(self, card_number):
        print('Transfer\nEnter card number:')
        new_number = input()
        if new_number == card_number:
            print('''You can't transfer money to the same account!''')
        elif new_number != self.luhn_algorithm(new_number[:-1]):
            print('''Probably you made a mistake in the card number. Please try again!''')
        elif not self.cur.execute('''SELECT EXISTS(SELECT 1 FROM card WHERE number = ?);''', (new_number,)).fetchone()[0]:
            print('''Such a card does not exist.''')
        else:
            print('''Enter how much money you want to transfer:''')
            amount = int(input())
            user_money = self.cur.execute('''SELECT balance FROM card WHERE number = ?;''', (card_number,)).fetchone()[0]
            if user_money < amount:
                print('Not enough money!')
            else:
                self.cur.execute('''UPDATE card SET balance = balance - ? WHERE number = ?;''', (amount, card_number))
                self.cur.execute('''UPDATE card SET balance = balance + ? WHERE number = ?;''', (amount, new_number))
                self.conn.commit()
                print('Success!')


if __name__ == '__main__':
    SimpleBankingSystem().main()
