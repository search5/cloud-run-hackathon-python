
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import random
from flask import Flask, request
from waitress import serve

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ['F', 'T', 'L', 'R']

self_state = {'x': 0, 'y': 0, 'direction': '', 'finish': True}


@app.route("/", methods=['GET'])
def index():
    return "Let the battle begin!"


def other_player_found(players, next_north_pos, next_west_pos, next_east_pos, next_south_pos, self_player):
    # 공격 대상 저장
    next_hit_player = None

    # 현재 내 위치에 가까운 플레이어를 찾아낸다
    for other_player in players:
        # 반복 중인 플레이어 상태가 F이거나 T일때만 골라낸다.(아 그리고 공격한 다음에 도망간다!!! TODO-나몰랑 귀차나)
        if (self_player['x'], next_north_pos) == (other_player['x'], other_player['y']):
            # north 위치의 적 확인
            next_hit_player = other_player
            break
        elif (next_west_pos, self_player['y']) == (other_player['x'], other_player['y']):
            # west 위치의 적 확인
            next_hit_player = other_player
            break
        elif (next_east_pos, self_player['y']) == (other_player['x'], other_player['y']):
            # east 위치의 적 확인
            next_hit_player = other_player
            break
        elif (self_player['x'], next_south_pos) == (other_player['x'], other_player['y']):
            # south 위치의 적 확인
            next_hit_player = other_player
            break
        else:
            # 인접한 네 방향에 적이 없을 수 있다.(TODO)
            pass
    return next_hit_player

@app.route("/", methods=['POST'])
def move():
    # request.get_data()
    req_json = request.get_json()
    self_link = req_json['_links']['self']['href']
    arena = request.get_json()['arena']
    dims = arena['dims']  # [10, 7]
    state = arena['state']

    self_player = state.pop(self_link)
    other_players = tuple(state.values())

    self_state.update({'x': self_player['x'],
                       'y': self_player['y'],
                       'direction': self_player['direction']})

    # F <- move Forward, R <- turn Right, L <- turn Left, T <- Throw

    # 현재 내 위치에 가까운 플레이어가 누군지 찾기 위해 나의 위치와 플레이어 위치를 비교한다
    # (단, 네 방향으로 3칸 단위로 존재하는지 확인)

    # ext_north_pos = self_player['y'] - 3
    # ext_west_pos = self_player['x'] - 3
    # ext_east_pos = self_player['x'] + 3
    # ext_south_pos = self_player['y'] + 3
    #
    # """
    # def other_player_found(players, next_north_pos, next_west_pos, next_east_pos, next_south_pos):
    #     # 공격 대상 저장
    #     next_hit_player = None
    #
    #     # 현재 내 위치에 가까운 플레이어를 찾아낸다
    #     for other_player in players:
    #         # 반복 중인 플레이어 상태가 F이거나 T일때만 골라낸다.(아 그리고 공격한 다음에 도망간다!!! TODO-나몰랑 귀차나)
    #         if (self_player['x'], next_north_pos) == (other_player['x'], other_player['y']):
    #             # north 위치의 적 확인
    #             next_hit_player = other_player
    #             break
    #         elif (next_west_pos, self_player['y']) == (other_player['x'], other_player['y']):
    #             # west 위치의 적 확인
    #             next_hit_player = other_player
    #             break
    #         elif (next_east_pos, self_player['y']) == (other_player['x'], other_player['y']):
    #             # east 위치의 적 확인
    #             next_hit_player = other_player
    #             break
    #         elif (self_player['x'], next_south_pos) == (other_player['x'], other_player['y']):
    #             # south 위치의 적 확인
    #             next_hit_player = other_player
    #             break
    #         else:
    #             # 인접한 네 방향에 적이 없을 수 있다.(TODO)
    #             pass
    #     return next_hit_player
    # """
    #
    # copy_north_pos = ext_north_pos
    # copy_west_pos = ext_west_pos
    # copy_east_pos = ext_east_pos
    # copy_south_pos = ext_south_pos
    #
    # next_hit_player = None
    #
    #
    # for i in range(3):
    #     next_hit_player = other_player_found(other_players, copy_north_pos, copy_west_pos, copy_east_pos, copy_south_pos, self_player)
    #     if not next_hit_player:
    #         # 공격자를 찾지 못하면... 한칸씩 줄여서 찾아본다.
    #         copy_north_pos -= 1
    #         copy_west_pos -= 1
    #         copy_east_pos -= 1
    #         copy_south_pos -= 1
    #
    # if next_hit_player:
    #     # 물폭탄 공격!!!
    #     return 'T'
    # else:
    #     # 공격할 대상을 찾지 못하면 다른 방향으로 방향을 틀고 이동한다(그러니까 실제로는 1칸 이동)
    #     # 아, 그 위치까지 플레이어들이 있으면 안된다. 그렇게 되면 이동할 수 없다.
    #     # 만약 사방향으로 플레이어가 있으면 플레이어가 없는 방향으로 R이나 L을 제공해야 한다.
    #     # 근데 만약 없으면?? 그냥 공격해버린다.
    #     # 물론, 나의 이전 direction이 R이거나 L일때 F 명령을 줘야 한다.
    #
    #     # 어느 방향에 적이 있는지 확인한다.
    #     warning_players = []
    #     for other_player in other_players:
    #         # 반복 중인 플레이어 상태가 F이거나 T일때만 골라낸다.
    #         if (self_player['x'], ext_north_pos) == (other_player['x'], other_player['y']):
    #             # north 위치의 적 확인
    #             warning_players.append('N')
    #         elif (ext_west_pos, self_player['y']) == (other_player['x'], other_player['y']):
    #             # west 위치의 적 확인
    #             warning_players.append('W')
    #         elif (ext_east_pos, self_player['y']) == (other_player['x'], other_player['y']):
    #             # east 위치의 적 확인
    #             warning_players.append('E')
    #         elif (self_player['x'], ext_south_pos) == (other_player['x'], other_player['y']):
    #             # south 위치의 적 확인
    #             warning_players.append('S')
    #
    #     if len(warning_players) == 4:
    #         return 'T'
    #     else:
    #         # 아.. 나의 이전 방향이 무엇인지에 따라 이동 방향을 결정해야 한다.
    #         # if self_player['direction'] == 'N':
    #         #     next_direction = ''
    #             # 적이 어느 방향에 있는지 확인한다.
    #
    #         # 적의 상태가 N이면 R을 반환한다
    #         # 적의 상태가 W이면 L을 반환한다
    #
    #         # N, W, E, S 방향에 적이 발견되는지 확인하여 적이 없는 방향으로 리턴한다.
    #         next_direction = ''
    #
    #         for iter_direction in warning_players:
    #             if iter_direction == 'N':
    #                 # 나의 직전 방향을 검사해서 방향을 튼다
    #                 if self_player['direction'] == 'N':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'W':
    #                     next_direction = 'L'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'E':
    #                     next_direction = 'R'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'S':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #             elif iter_direction == 'W':
    #                 if self_player['direction'] == 'N':
    #                     next_direction = 'R'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'W':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'E':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'S':
    #                     next_direction = 'L'
    #                     self_state['finish'] = False
    #             elif iter_direction == 'E':
    #                 if self_player['direction'] == 'N':
    #                     next_direction = 'L'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'W':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'E':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'S':
    #                     next_direction = 'R'
    #                     self_state['finish'] = False
    #             elif iter_direction == 'S':
    #                 if self_player['direction'] == 'N':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'W':
    #                     next_direction = 'R'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'E':
    #                     next_direction = 'L'
    #                     self_state['finish'] = False
    #                 elif self_player['direction'] == 'S':
    #                     next_direction = ('R', 'L')[random.randrange(2)]
    #                     self_state['finish'] = False
    #
    #         # 내가 이전했는지 아닌지 알려면.. 나의 직전 위치를 가지고 있어야 한다.. 하아.. 야이..
    #         if self_state['direction'] == next_direction and not self_state['finish']:
    #             return 'F'
    #         elif self_state['direction'] == next_direction and self_state['finish']:
    #             self_state['finish'] = False
    #             return moves[random.randrange(len(moves))]
    #         else:
    #             return next_direction

    # {
    #   'x': 9,
    #   'y': 0,
    #   'direction': 'S',
    #   'wasHit': False,
    #   'score': -10
    # }


    return moves[random.randrange(len(moves))]

if __name__ == "__main__":
    # app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
    serve(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
