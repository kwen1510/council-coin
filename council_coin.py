# pip install qrcode
# pip install Pillow

import qrcode

def generate_qr_code(studentID):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=10,
        border=4,
    )
    qr.add_data(studentID)
    qr.make(fit=True)

    image = qr.make_image(fill_color="blue", back_color="white")
    image.save(f'QR_Codes/{studentID}.png')


# # Generate one QR code
# generate_qr_code("kuangwen")


userID_list = [12345,23456,'kuangwen']

for userID in userID_list:
	generate_qr_code(userID)
