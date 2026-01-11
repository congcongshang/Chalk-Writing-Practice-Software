import pygame
import random
import sys
import imageio
import os

# 初始化Pygame
pygame.init()

# 屏幕设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("粉笔字+粉笔末效果 - 空格录制/保存，右键清屏 | 流畅版")

# 离屏表面保存笔迹
drawing_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
drawing_surface.fill((0, 0, 0, 0))

# 颜色定义（恢复自然对比度）
BLACKBOARD = (20, 25, 30)
CHALK_WHITE = (240, 240, 230)
CHALK_YELLOW = (245, 240, 200)

# 粒子类（粉笔屑：调回自然下落参数）
class ChalkDust:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 2)  # 恢复1-2像素，更有颗粒感
        self.color = random.choice([CHALK_WHITE, CHALK_YELLOW])
        self.speed_y = random.uniform(1.0, 2.5)  # 下落速度更自然
        self.speed_x = random.uniform(-0.5, 0.5)  # 横向飘移更明显
        self.life = random.randint(20, 70)  # 生命周期更长，下落更完整

    def update(self):
        self.y += self.speed_y
        self.x += self.speed_x
        self.speed_y += 0.03  # 重力加速适中，下落有轻重感
        self.life -= 1

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

# 主程序变量
clock = pygame.time.Clock()
drawing = False
last_pos = None
brush_size = 4  # 细腻笔触，保证写字流畅
dust_count = 2  # 恢复2个/帧，粉笔屑更密集自然
dust_list = []

# 录屏优化：渲染帧率120，录制抽帧（避免内存爆掉）
recording = False
frame_list = []
MAX_RECORD_FRAMES = 300  # 最终GIF最多300帧（对应20秒@15帧/秒）
record_frame_step = 5    # 每4帧存1帧（120渲染帧 → 30录制帧/秒 → 导出时降为15）
frame_counter = 0        # 帧计数器，用于抽帧

# 自动获取桌面路径
gif_path = os.path.join(os.path.expanduser("~"), "Desktop", "粉笔字效果.gif")

# 主循环
running = True
while running:
    # 渲染帧率拉回120 → 写字丝滑无延迟
    clock.tick(120)
    screen.fill(BLACKBOARD)
    frame_counter += 1

    # 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 鼠标事件
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                drawing = True
                last_pos = pygame.mouse.get_pos()
            elif event.button == 3:
                drawing_surface.fill((0, 0, 0, 0))
                dust_list.clear()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False
                last_pos = None
        
        # 空格键：开始/停止录制
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not recording:
                    recording = True
                    frame_list.clear()
                    frame_counter = 0
                    print(f"开始录制！写字超流畅~ 再次按空格保存GIF | 最多录制{MAX_RECORD_FRAMES//15}秒")
                else:
                    recording = False
                    if len(frame_list) == 0:
                        print("无录制内容！")
                        continue
                    try:
                        imageio.mimsave(gif_path, frame_list, duration=1/15, loop=0)
                        print(f"GIF保存成功 → {gif_path}")
                    except Exception as e:
                        print(f"保存失败：{str(e)}")

    # 绘制逻辑：120帧渲染 → 写字无间隙、超流畅
    if drawing:
        current_pos = pygame.mouse.get_pos()
        if last_pos and current_pos != last_pos:
            # 连续线条：笔触细腻，无断点
            pygame.draw.line(drawing_surface, CHALK_WHITE, last_pos, current_pos, brush_size)
            # 纹理点：少量但自然
            for _ in range(1):
                offset_x = random.randint(-brush_size//2+1, brush_size//2+1)
                offset_y = random.randint(-brush_size//2+1, brush_size//2+1)
                texture_x = current_pos[0] + offset_x
                texture_y = current_pos[1] + offset_y
                texture_color = random.choice([CHALK_WHITE, CHALK_YELLOW])
                pygame.draw.circle(drawing_surface, texture_color, (texture_x, texture_y), 1)
            # 生成粉笔屑：数量适中，下落飘逸
            for _ in range(dust_count):
                dust = ChalkDust(current_pos[0], current_pos[1])
                dust_list.append(dust)
            last_pos = current_pos

    # 更新粉笔屑：下落效果自然，有飘动感
    for dust in dust_list[:]:
        dust.update()
        dust.draw()
        if dust.life <= 0:
            dust_list.remove(dust)

    # 绘制笔迹
    screen.blit(drawing_surface, (0, 0))
    pygame.display.flip()

    # 录制逻辑：抽帧保存 → 不占内存，不影响流畅度
    if recording:
        # 每4帧存1帧，120渲染帧 → 30录制帧/秒，导出时降为15帧/秒
        if frame_counter % record_frame_step == 0:
            if len(frame_list) < MAX_RECORD_FRAMES:
                frame = pygame.surfarray.array3d(screen)
                frame = frame.transpose(1, 0, 2)
                frame_list.append(frame)
            else:
                recording = False
                print(f"达到最大时长！自动保存GIF → {gif_path}")
                try:
                    imageio.mimsave(gif_path, frame_list, duration=1/15, loop=0)
                except:
                    pass

# 退出程序
pygame.quit()
sys.exit()