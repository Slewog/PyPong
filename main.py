from sys import exit
import pygame as pg
from time import time

from settings import FPS, SCREEN_W, SCREEN_H , MAX_SCORE, FONT_COLOR, FONT_SIZE, MIDDLE_LINE_W
from settings import OBJECT_COLOR, BACKGROUND_COLOR, FONT_COLOR, HIT_SOUND_VOL, SCORE_SOUND_VOL
from locales import Locales
from sprites import Ball, Player
from utils import load_color, load_sound


class Pong:
    FPS = FPS
    SCREEN_H = SCREEN_H
    SCREEN_MH = SCREEN_H // 2
    SCREEN_W = SCREEN_W
    SCREEN_MW = SCREEN_W // 2
    MAX_SCORE = MAX_SCORE

    def __init__(self) -> None:
        pg.mixer.pre_init(44100, -16, 2, 512)
        pg.init()

        self.clock = pg.time.Clock()

        self.display_surf = pg.display.set_mode((self.SCREEN_W, self.SCREEN_H))
        pg.display.set_caption(Locales.GAME_NAME)

        self.winned = bool(False)
        self.playing = bool(False)

        self.all_sprites = pg.sprite.Group()

    def load_assets(self) -> None:
        self.font = pg.font.Font('freesansbold.ttf', FONT_SIZE)
        self.font_color = load_color(FONT_COLOR)
        self.obj_color = load_color(OBJECT_COLOR)
        self.bg_color = load_color(BACKGROUND_COLOR)

        self.display_surf.fill(self.bg_color)
        pg.display.flip()

        self.middle_line_w = MIDDLE_LINE_W
        self.middle_line = pg.Rect(self.SCREEN_MW - self.middle_line_w//2, int(0), self.middle_line_w, self.SCREEN_H)

        self.win_txt_pos = (self.SCREEN_MW, self.SCREEN_MH - 70)
        self.start_txt = self.font.render(
            Locales.START_TXT, True, self.font_color)
        self.start_txt_rect = self.start_txt.get_rect(
            center=(self.SCREEN_MW, self.SCREEN_MH + 60))
        self.start_txt_bg = pg.Rect(self.start_txt_rect.x, self.start_txt_rect.y - 2,
                                    self.start_txt_rect.width, self.start_txt_rect.height)

        self.restart_txt = self.font.render(
            Locales.RESTART_TXT, True, self.font_color)
        self.restart_txt_rect = self.restart_txt.get_rect(
            center=(self.SCREEN_MW, self.SCREEN_MH + 60))
        self.restart_txt_bg = pg.Rect(self.restart_txt_rect.x, self.restart_txt_rect.y - 2,
                                      self.restart_txt_rect.width, self.restart_txt_rect.height)

        hit_sound = load_sound('pong.ogg', HIT_SOUND_VOL)
        score_sound = load_sound('score.ogg', SCORE_SOUND_VOL)

        self.player_left = Player('left', Locales.PLAYER_LEFT, self.SCREEN_W, self.SCREEN_H,
                                  self.SCREEN_MH, self.all_sprites, self.font, self.font_color, self.obj_color)
        self.player_right = Player('right', Locales.PLAYER_RIGHT, self.SCREEN_W, self.SCREEN_H,
                                   self.SCREEN_MH, self.all_sprites, self.font, self.font_color, self.obj_color)
        self.players: list[Player] = [self.player_left, self.player_right]

        self.ball = Ball(self.SCREEN_W, self.SCREEN_H, self.SCREEN_MW, self.SCREEN_MH, self.font, self.font_color,
                         self.obj_color, self.all_sprites, self.player_left, self.player_right, self.MAX_SCORE, [hit_sound, score_sound])

    def quit(self):
        for sprite in self.all_sprites:
            sprite: Player | Ball
            sprite.kill()

        pg.quit()
        exit()

    def reset(self, player_dir: bool) -> None:
        if player_dir:
            for player in self.players:
                player.reset_direction(False)
            return

        for player in self.players:
            player.reset()

        self.ball.reset(True)
        self.winned = bool(False)

    def start(self) -> None:
        self.playing = bool(True)
        self.ball.freeze_time = pg.time.get_ticks()

    def render_frame(self) -> None:
        pg.draw.rect(self.display_surf, self.font_color, self.middle_line)
        self.all_sprites.draw(self.display_surf)

        for player in self.players:
            player.draw_hud(self.display_surf)

        if self.winned:
            pg.draw.rect(self.display_surf, self.bg_color, self.win_text_rect)
            self.display_surf.blit(self.win_text, self.win_text_rect)
            pg.draw.rect(self.display_surf, self.bg_color, self.restart_txt_bg)
            self.display_surf.blit(self.restart_txt, self.restart_txt_rect)

        if not self.playing:
            pg.draw.rect(self.display_surf, self.bg_color, self.start_txt_bg)
            self.display_surf.blit(self.start_txt, self.start_txt_rect)

        if self.playing and not self.ball.active and self.ball.freeze_time != 0:
            self.ball.draw_restart_counter(self.display_surf, self.bg_color) 
        
    def run(self) -> None:
        self.load_assets()
        prev_dt = time()

        while True:
            self.clock.tick(self.FPS)

            for e in pg.event.get():
                if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                    self.quit()

                if self.playing and self.winned and e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                    self.reset(False)

                if not self.playing and e.type == pg.KEYDOWN and e.key == pg.K_SPACE:
                    self.start()

            self.display_surf.fill(self.bg_color)

            current_time = time()
            dt = current_time - prev_dt
            prev_dt = current_time

            if self.playing and not self.winned:
                keys = pg.key.get_pressed()

                for player in self.players:
                    player.check_input(keys)

                    if not self.winned and player.score == self.MAX_SCORE:
                        self.win_text = self.font.render(Locales.WIN_TXT.format(
                            player=player.side_trslt), True, self.font_color)

                        self.win_text_rect = self.win_text.get_rect(
                            center=self.win_txt_pos)

                        self.winned = bool(True)
                        self.reset(True)

                if not self.ball.active and self.ball.freeze_time != 0:
                    self.ball.check_freeze_time()

            self.all_sprites.update(dt)

            self.render_frame()

            pg.display.flip()


if __name__ == '__main__':
    Pong().run()
