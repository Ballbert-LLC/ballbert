#!/bin/bash
cd Skills

read -p "Skill name: " name
read -p "Author name: " author

mkdir "$name"
cd "$name"

echo "from .$name import $name" > __init__.py 

config=$(cat <<EOF
name: $name
author: $author
version: 0.0.1
EOF
)

echo "$config" > config.yaml

echo "{}" > settings.yaml

settings_meta=$(cat <<EOF
EOF
)

echo "$settings_meta" > settingsmeta.yaml

python_code=$(cat <<EOF
from Hal.Classes import Response
from Hal.Decorators import reg
from Hal.Skill import Skill

class $name(Skill):
    def __init__(self):
        pass

    @reg(name="your_skill_name")
    def your_skill_name(self, required_param, optional_param="default value"):
        """
        your_skill_name description

        :param string required_param: The required param description
        :param string optional_param: (Optional) The optional param description
        """
        
        return Response(True, data="result data")
EOF
)

echo "$python_code" > "$name.py"
