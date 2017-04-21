#coding:utf-8

import encrypt

out_boot_path = "../Resources/boot.oxgame"
out_game_path = "../Resources/game.bin"

if __name__ == '__main__':

    encrypt.decrypt_file(out_boot_path)
    encrypt.decrypt_file(out_game_path)
    print("------- over --------")