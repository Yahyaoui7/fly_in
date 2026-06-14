VALID_CATEGORIES=("easy" "medium" "hard" "challenger")

echo "========================================="
echo "   RUNNING VALID MAPS (Should Pass)      "
echo "========================================="

for cat in "${VALID_CATEGORIES[@]}"; do
    if [ -d "maps/$cat" ]; then
        echo -e "\n--- Category: ${cat^^} ---"
        for map in maps/"$cat"/*.txt; do
             echo $map
            [ -e "$map" ] || continue
            echo "[RUNNING] python main.py "$map""
            python3 main.py "$map"
            echo "-----------------------------------------"
        done
    fi
done

echo -e "\n========================================="
echo "   RUNNING ERROR MAPS (Should Fail/Error)"
echo "========================================="

if [ -d "maps/error" ]; then
    for map in maps/error/*.txt; do
        [ -e "$map" ] || continue
        echo "[TESTING ERROR] python main.py "$map""
        python3 main.py "$map"
        echo "-----------------------------------------"
    done
else
    echo "No maps/error directory found."
fi
