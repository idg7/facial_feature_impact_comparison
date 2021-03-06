import os
import shutil

def transfer_datapoints(dest_dataset_loc, phase, data_class, data_points):
    dest_dir = os.path.join(dest_dataset_loc, phase, data_class)

    os.makedirs(dest_dir)
    for source_point in data_points:
        # source_point = os.path.join(source_dataset_loc, data_class, point)
        dest_point = os.path.join(dest_dir, os.path.basename(source_point))

        try:
            os.symlink(source_point, dest_point)
        except OSError:
            shutil.copyfile(source_point, dest_point)
