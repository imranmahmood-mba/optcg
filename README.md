# One Piece Trading Card Game Data Pipeline(optcg)

*by Imran Mahmood*

---

## Introduction

This is a pipeline that takes data from tcgplayer.com and scrapes all of the One Piece TCG card data and adds it to a csv file. The script then loads the data into an s3 bucket which then triggers a lambda function whic automatically loads the data into a MySQL RDS instance.


