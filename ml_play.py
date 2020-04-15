"""
The template of the main script of the machine learning process
"""
import numpy as np
import pickle
import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
n = 0
def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """
    ball_pos_history = []
    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        ball_pos_history.append(scene_info.ball)
        #判定球為上升還是落下
        if (len(ball_pos_history)) == 1:
            ball_godown = 0
        elif ball_pos_history[-1][1] - ball_pos_history[-2][1] > 0: #[-1]代表倒數最後一列
            ball_godown = 1
            vy = ball_pos_history[-1][1]-ball_pos_history[-2][1]
            vx = ball_pos_history[-1][0]-ball_pos_history[-2][0]
            m = vy/vx
        else:
            ball_godown = 0

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            ball_x = scene_info.ball[0] #the x of tuple(x, y)
            ball_y = scene_info.ball[1]
            platform_x = scene_info.platform[0]
            if ball_godown == 1 and ball_y >= 45:
                final_x = (400 - ball_y)/m + ball_x
                if final_x > 200:
                    final_x = 200 - (final_x - 200)
                elif final_x < 0:
                    final_x = -final_x
                if final_x > platform_x + 40:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                elif final_x < platform_x:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)