from telethon.sync import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    PasswordHashInvalidError,
)
from telethon.sessions import StringSession


def generate_session():
    print("Welcome to Telegram String Session Generator!\n")

    # Step 1: Input API credentials
    api_id = input("Enter your API ID: ").strip()
    api_hash = input("Enter your API Hash: ").strip()

    # Initialize client
    client = TelegramClient(StringSession(), api_id, api_hash)

    # Step 2: Input phone number
    phone_number = input("\nEnter your phone number (with country code): ").strip()

    try:
        # Connect to Telegram
        client.connect()
        if not client.is_user_authorized():
            # Send OTP
            print("\nSending OTP to your phone...")
            client.send_code_request(phone_number)

            # Step 3: Input OTP
            otp = input("\nEnter the OTP you received (e.g., '1 2 3 4 5'): ").strip().replace(" ", "")
            try:
                client.sign_in(phone_number, otp)
            except SessionPasswordNeededError:
                # Step 4: Handle two-step verification
                password = input("\nTwo-step verification is enabled. Enter your password: ").strip()
                try:
                    client.sign_in(password=password)
                except PasswordHashInvalidError:
                    print("\nInvalid password. Please try again.")
                    return
            except PhoneCodeInvalidError:
                print("\nInvalid OTP. Please try again.")
                return
        # Generate session string
        session_string = client.session.save()
        print("\nYour String Session:")
        print(session_string)
        print("\nKeep this string session safe! Do not share it with anyone.")
    except PhoneNumberInvalidError:
        print("\nInvalid phone number. Please check and try again.")
    finally:
        client.disconnect()


if __name__ == "__main__":
    generate_session()
