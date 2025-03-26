
import random
import pygame
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button

# تهيئة pygame للمؤثرات الصوتية
pygame.mixer.init()

class GameWidget(Widget):
    def __init__(self, **kwargs):
        super(GameWidget, self).__init__(**kwargs)

        # تهيئة المتغيرات
        self.player_pos = (Window.width // 2, 50)
        self.bullets = []
        self.enemies = []
        self.enemy_speed = 3
        self.bullet_speed = 10
        self.game_over = False
        self.level = 1
        self.enemy_spawn_rate = 1
        self.enemies_killed = 0
        self.max_enemies = 5

        # تحميل الصوتيات
        self.shoot_sound = pygame.mixer.Sound('shoot.wav')
        self.explosion_sound = pygame.mixer.Sound('explosion.wav')

        # رسم اللاعب مع صورة
        with self.canvas:
            self.player = Rectangle(pos=self.player_pos, size=(50, 50), source='player.png')

        # إنشاء أعداء
        Clock.schedule_interval(self.create_enemy, self.enemy_spawn_rate)
        Clock.schedule_interval(self.update, 1.0 / 60.0)  # 60 FPS

    def on_touch_move(self, touch):
        if not self.game_over:
            self.player_pos = (touch.x - 25, 50)  # يتحرك اللاعب مع الإصبع
            self.player.pos = self.player_pos

    def shoot(self):
        if not self.game_over:
            # إطلاق رصاصة
            bullet = Ellipse(pos=(self.player_pos[0] + 20, self.player_pos[1] + 50), size=(10, 20))
            self.bullets.append(bullet)
            # تشغيل صوت الإطلاق
            self.shoot_sound.play()

    def create_enemy(self, dt):
        if not self.game_over and len(self.enemies) < self.max_enemies:
            # إنشاء عدو عشوائي
            enemy_pos = (random.randint(0, Window.width - 50), Window.height - 50)
            with self.canvas:
                enemy = Rectangle(pos=enemy_pos, size=(50, 50), source='enemy.png')
            self.enemies.append(enemy)

    def update(self, dt):
        if self.game_over:
            return

        # تحريك الرصاصات للأعلى
        for bullet in self.bullets[:]:
            bullet.pos = (bullet.pos[0], bullet.pos[1] + self.bullet_speed)
            if bullet.pos[1] > Window.height:
                self.bullets.remove(bullet)

        # تحريك الأعداء للأسفل
        for enemy in self.enemies[:]:
            enemy.pos = (enemy.pos[0], enemy.pos[1] - self.enemy_speed)
            if enemy.pos[1] < 0:
                self.enemies.remove(enemy)

        # كشف التصادم بين الرصاصات والأعداء
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collide_widget(enemy):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    # تشغيل صوت الانفجار
                    self.explosion_sound.play()
                    self.enemies_killed += 1
                    if self.enemies_killed % 5 == 0:
                        self.level_up()
                    break  # خروج من اللوب بعد التصادم

        # إذا اصطدم العدو باللاعب
        for enemy in self.enemies[:]:
            if self.player.collide_widget(enemy):
                self.game_over = True
                self.display_game_over()

    def level_up(self):
        self.level += 1
        self.enemy_speed += 1
        self.enemy_spawn_rate -= 0.1  # زيادة سرعة الأعداء وتقليل الزمن بين ظهورهم
        self.max_enemies += 2  # زيادة عدد الأعداء في كل مرحلة
        Clock.unschedule(self.create_enemy)
        Clock.schedule_interval(self.create_enemy, self.enemy_spawn_rate)

        # تحديث مستوى اللعبة
        level_up_label = Label(text=f"Level {self.level}", font_size=50, pos=(Window.width//3, Window.height//1.5))
        self.add_widget(level_up_label)
        Clock.schedule_once(lambda dt: self.remove_widget(level_up_label), 1)

    def display_game_over(self):
        self.game_over_label = Label(text="Game Over", font_size=50, pos=(Window.width//3, Window.height//2))
        self.add_widget(self.game_over_label)
        restart_button = Button(text='Restart', size=(200, 50), pos=(Window.width//3, Window.height//3))
        restart_button.bind(on_press=self.restart_game)
        self.add_widget(restart_button)

    def restart_game(self, instance):
        self.bullets = []
        self.enemies = []
        self.game_over = False
        self.level = 1
        self.enemy_speed = 3
        self.enemy_spawn_rate = 1
        self.enemies_killed = 0
        self.max_enemies = 5
        self.remove_widget(self.game_over_label)
        self.remove_widget(instance)
        self.player_pos = (Window.width // 2, 50)
        self.player.pos = self.player_pos

    def on_touch_down(self, touch):
        if not self.game_over:
            self.shoot()

class GameApp(App):
    def build(self):
        game_widget = GameWidget()
        return game_widget

if __name__ == '__main__':
    GameApp().run()
