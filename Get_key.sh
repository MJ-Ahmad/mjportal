Get_Key() {
    clear

    CYAN='\033[1;36m'
    YELLOW='\033[1;33m'
    GREEN='\033[1;32m'
    MAGENTA='\033[1;35m'
    NC='\033[0m'

    keys=(
        "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"
    )

    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}         SAMPLE PASSWORD KEYS${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo

    i=1
    for key in "${keys[@]}"; do
        printf "${GREEN}[%d] %s${NC}\n" "$i" "$key"
        ((i++))
    done

    echo
    echo -e "${CYAN}========================================${NC}"
    echo -e "${MAGENTA}Total Keys: ${#keys[@]}${NC}"
    echo -e "${CYAN}========================================${NC}"
}
