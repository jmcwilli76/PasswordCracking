import GPGMail
import time

KeepLooping = True
while (KeepLooping):
    print("Processing.")
    GPGMail.main()
    time.sleep(60)
