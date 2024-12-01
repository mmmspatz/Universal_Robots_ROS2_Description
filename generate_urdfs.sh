#!/bin/bash

# Generate a URDF file for each robot type from ur.urdf.xacro

DOCKERFILE=$(cat <<'EOF'
FROM ros:iron-ros-base

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install \
    ros-iron-xacro \
    && rm -rf /var/lib/apt/lists/
EOF
)

COMMAND=$(cat <<'EOF'
#!/bin/bash

# Need to install the package in order for xacro to see resources inside of it
colcon --log-base /dev/null build --symlink-install --install-base /tmp/ur_description_install --build-base /tmp/ur_description_build
source /tmp/ur_description_install/local_setup.bash

# Loop through each robot type and run the xacro command
cd urdf
robot_types=("ur3" "ur3e" "ur5" "ur5e" "ur10" "ur10e" "ur16e" "ur20" "ur30")
for ur_type in "${robot_types[@]}"; do
    xacro ur.urdf.xacro name:="$ur_type" ur_type:="$ur_type" > "$ur_type.urdf"
    echo "Generated $ur_type.urdf"
done
EOF
)

IMAGE=urdf_builder
docker build -t "$IMAGE" - <<< "$DOCKERFILE"
docker run --rm -v "$PWD:/workdir" -w /workdir "$IMAGE" bash -c "$COMMAND"
