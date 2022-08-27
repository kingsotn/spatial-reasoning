#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in    the
# LICENSE file in the root directory of this source tree.


import argparse
import demo_runner as dr

import math
import numpy as np


from collections import defaultdict

import PIL

parser = argparse.ArgumentParser()
parser.add_argument("--scene", type=str, default=dr.default_sim_settings["scene"])
parser.add_argument("--width", type=int, default=640)
parser.add_argument("--height", type=int, default=480)
parser.add_argument("--max_frames", type=int, default=5)
parser.add_argument("--save_png", action="store_true")
parser.add_argument("--sensor_height", type=float, default=1.5)
parser.add_argument("--disable_color_sensor", action="store_true")
parser.add_argument("--semantic_sensor", action="store_true")
parser.add_argument("--depth_sensor", action="store_true")
parser.add_argument("--print_semantic_scene", action="store_true")
parser.add_argument("--print_semantic_mask_stats", action="store_true")
parser.add_argument("--compute_shortest_path", action="store_true")
parser.add_argument("--compute_action_shortest_path", action="store_true")
parser.add_argument("--recompute_navmesh", action="store_true")
parser.add_argument("--seed", type=int, default=1)
parser.add_argument("--silent", action="store_true")
parser.add_argument("--test_fps_regression", type=int, default=0)
parser.add_argument("--enable_physics", action="store_true")
parser.add_argument(
    "--physics_config_file",
    type=str,
    default=dr.default_sim_settings["physics_config_file"],
)
parser.add_argument("--disable_frustum_culling", action="store_true")
args = parser.parse_args()


def make_settings():
    settings = dr.default_sim_settings.copy()
    settings["max_frames"] = args.max_frames
    settings["width"] = args.width
    settings["height"] = args.height
    settings["scene"] = args.scene
    settings["save_png"] = args.save_png
    settings["sensor_height"] = args.sensor_height
    settings["color_sensor"] = not args.disable_color_sensor
    settings["semantic_sensor"] = args.semantic_sensor
    settings["depth_sensor"] = args.depth_sensor
    settings["print_semantic_scene"] = args.print_semantic_scene
    settings["print_semantic_mask_stats"] = args.print_semantic_mask_stats
    settings["compute_shortest_path"] = args.compute_shortest_path
    settings["compute_action_shortest_path"] = args.compute_action_shortest_path
    settings["seed"] = args.seed
    settings["silent"] = args.silent
    settings["enable_physics"] = args.enable_physics
    settings["physics_config_file"] = args.physics_config_file
    settings["frustum_culling"] = not args.disable_frustum_culling
    settings["recompute_navmesh"] = args.recompute_navmesh

    return settings


settings = make_settings()

perfs = []
world_coord = defaultdict(list)

for _i in range(1):
    demo_runner = dr.DemoRunner(settings, dr.DemoRunnerType.EXAMPLE)
    perf, depth_image, pose= demo_runner.example()
    perfs.append(perf)

    print(" ========================= Performance ======================== ")
    print(
        " %d x %d, total time %0.2f s,"
        % (settings["width"], settings["height"], perf["total_time"]),
        "frame time %0.3f ms (%0.1f FPS)" % (perf["frame_time"] * 1000.0, perf["fps"]),
    )
    print(" ============================================================== ")



    print(" \n ========================= Obtain World Coord ======================== ")

    # assert perf["fps"] > args.test_fps_regression, (
    #    "FPS is below regression threshold: %0.1f < %0.1f"
    #    % (perf["fps"], args.test_fps_regression)
    # )

    # Constants from settings.py
    HFOV = settings["hfov"]
    WIDTH = settings["width"]
    HEIGHT = settings["height"]

    # focal length in pixels
    FOCAL_LENGTH = WIDTH / (2 * math.tan(HFOV/2))

    # image center cx,cy coord
    CX = int(WIDTH / 2)
    CY = int(HEIGHT / 2)

    # convert raw depth_image to depth_image_pixels
    depth_image_pixels = []
    for image in depth_image:
        pixel_array = np.array(image)
        depth_image_pixels.append(pixel_array)


    # index, pixel, image num, are all indexed from 0
    ROUND_NUMBERS = True
    world_coord_list = []
    for index, pixel_depth in np.ndenumerate(depth_image_pixels):
        image_id, x, y = index[0], index[1], index[2]
        X_world = (x - CX) * pixel_depth / FOCAL_LENGTH                             
        Y_world = (y - CY) * pixel_depth / FOCAL_LENGTH
        Z_world = pixel_depth

        if x == 0 and y == 0:
            world_coord_list.append(f"image_id: {image_id}")
            print(f"\rProgress: [{'#'*(image_id)}] {round((image_id)/len(depth_image_pixels), 3)*100}%")

        if ROUND_NUMBERS:
            X_world, Y_world = round(X_world, 3), round(Y_world, 3)

        world_coord_list.append(f"Pixel [{x},{y}] \n \t {(X_world, Y_world, Z_world)}")
        
    with open("world_coord.txt", "w") as f:
        for item in world_coord_list:
            f.write("%s\n" % item)
    print(" \n ========================= End Obtain World Coord ======================== ")



if len(perfs) > 1:
    avg_fps = 0
    avg_frame_time = 0
    avg_step_time = 0
    print("all perfs: " + str(perfs))
    for perf in perfs:
        print("----")
        print(perf["time_per_step"])
        avg_fps += perf["fps"]
        avg_frame_time += perf["frame_time"]
        for step_time in perf["time_per_step"]:
            avg_step_time += step_time
    avg_fps /= len(perfs)
    avg_frame_time /= len(perfs)
    avg_step_time /= len(perfs) * len(perfs[0]["time_per_step"])
    print("Average FPS: " + str(avg_fps))
    print("Average frame time: " + str(avg_frame_time))
    print("Average step time: " + str(avg_step_time))