"""
SoFIFA Player Scraper
Comprehensive scraper using modular PlayerScraper
"""
import argparse
import csv
import asyncio
import re
from playwright.async_api import async_playwright
from player_scraper import PlayerScraper


class SoFIFAScraper:
    def __init__(self, player_urls_file="player_urls.csv", output_file="player_stats.csv"):
        self.player_urls_file = player_urls_file
        self.output_file = output_file
        self.player_urls = []
        self.player_stats = []
        self.columns = None
        self.csv_initialized = False

    def load_player_urls(self):
        """Load player URLs from CSV file"""
        print(f"Loading player URLs from {self.player_urls_file}...")
        with open(self.player_urls_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            self.player_urls = [row[0] for row in reader if row]
            self.player_urls = self.player_urls[:100]

        print(f"Loaded {len(self.player_urls)} player URLs")
        return self.player_urls

    async def scrape_player_stats(self, max_players=None):
        """Scrape detailed stats for each player"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)' \
                ' Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            )
            
            page = await context.new_page()
            
            # Block images, stylesheets, fonts to optimize loading
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_())
            
            urls_to_scrape = self.player_urls[:max_players] if max_players else self.player_urls
            total = len(urls_to_scrape)
            
            # === 添加版本号循环列表（第 73 行左右） ===
            version_codes = [
                240000, 240003, 240012, 240016, 240019, 240024,
                240028, 240034, 240038, 240041, 240045, 240048,
                240049, 250003, 250007, 250012, 250015, 250018,
                250023, 250030, 250034, 250036, 250040, 250044
            ]

            for idx, url in enumerate(urls_to_scrape, 1):
                player_name = None  # 用来记录当前球员名字
                for version in version_codes:
                    base_url = re.sub(r'/\d+/?$', '', url)  # 去掉旧的版本号
                    version_url = f"{base_url.rstrip('/')}/{version}/"

                    retries = 0
                    max_retries = 5
                    success = False

                    while retries < max_retries and not success:
                        try:
                            if retries > 0:
                                print(f"  Retry {retries}/{max_retries} after 10s pause...")
                                await asyncio.sleep(10)
                    
                            await page.goto(version_url, wait_until="domcontentloaded", timeout=15000)
                            await page.wait_for_timeout(2000)
                        
                            # Check for Cloudflare challenge
                            page_content = await page.content()
                            if 'Checking your browser' in page_content or 'Just a moment' in page_content or 'cf-browser-verification' in page_content:
                                print("  ⚠ Cloudflare challenge detected")
                                retries += 1
                                continue
                        
                            # Extract player stats using modular scraper
                            stats = await PlayerScraper.scrape_player_data(page, version_url)
                            stats["version"] = version

                            if stats.get('name'):
                                player_name = stats.get('name')
                                self.player_stats.append(stats)
                                # Save incrementally after each player
                                self.save_player_by_id(stats)
                                success = True
                            else:
                                print("  ✗ No data extracted")
                                retries += 1
                            
                        except Exception as e:
                            print(f"  ✗ Error: {str(e)}")
                            retries += 1
                
                    if not success:
                        print(f"  ✗ Failed after {max_retries} retries, skipping...")
                # ✅ 所有版本爬完后再报告一次
                if player_name:
                    print(f"  💾 Finished saving all versions for {player_name}")
            await browser.close()

    def _get_column_order(self, stats_dict):
        """Define and return the column order for CSV"""
        priority_cols = [
            'player_id', 'version', 'name', 'full_name', 'description', 'image',
            'height_cm', 'weight_kg', 'dob', 'positions', 'overall_rating', 'potential',
            'value', 'wage', 'preferred_foot', 'weak_foot', 'skill_moves',
            'international_reputation', 'body_type', 'real_face',
            'release_clause', 'specialities', 'club_id', 'club_name', 'club_league_id',
            'club_league_name', 'club_logo', 'club_rating', 'club_position',
            'club_kit_number', 'club_joined', 'club_contract_valid_until',
            'country_id', 'country_name', 'country_league_id', 'country_league_name',
            'country_flag', 'country_rating', 'country_position', 'country_kit_number',
            'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy', 
            'attacking_short_passing', 'attacking_volleys',
            'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing', 
            'skill_ball_control',
            'movement_acceleration', 'movement_sprint_speed', 'movement_agility', 
            'movement_reactions', 'movement_balance',
            'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength', 
            'power_long_shots',
            'mentality_aggression', 'mentality_interceptions', 'mentality_att_positioning', 
            'mentality_vision', 'mentality_penalties', 'mentality_composure',
            'defending_defensive_awareness', 'defending_standing_tackle', 'defending_sliding_tackle',
            'goalkeeping_gk_diving', 'goalkeeping_gk_handling', 'goalkeeping_gk_kicking', 
            'goalkeeping_gk_positioning', 'goalkeeping_gk_reflexes',
            'play_styles', 'url'
        ]
        
        # Add priority columns first, then any additional columns
        all_keys = set(stats_dict.keys())
        other_cols = sorted([col for col in all_keys if col not in priority_cols])
        columns = [col for col in priority_cols if col in all_keys] + other_cols
        return columns
    
    def save_player_to_csv(self, stats):
        """Save a single player's stats to CSV file incrementally"""
        import os
        
        # Check if file exists
        file_exists = os.path.isfile(self.output_file) and self.csv_initialized
        
        # Initialize columns on first write
        if self.columns is None:
            self.columns = self._get_column_order(stats)
        
        # Write to CSV
        mode = 'a'
        if not self.csv_initialized:
            mode = 'w'
            self.csv_initialized = True

        with open(self.output_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.columns)
            
            # Write header only if file doesn't exist
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(stats)

    def save_player_by_id(self, stats):
        """Save one player's all versions to a separate CSV file"""
        import os

        os.makedirs("data", exist_ok=True)
        player_id = stats.get("player_id", "unknown")
        name = stats.get("name", "unknown").replace(" ", "_").replace(".", "")
        filename = f"data/{name}_{player_id}_sofifa_ratings.csv"

        columns = [
            'version', 'name',
            'height_cm', 'weight_kg', 'dob', 'positions', 'overall_rating', 'potential','value', 'wage', 
            'preferred_foot', 'weak_foot', 'skill_moves', 'international_reputation', 'body_type', 
            'club_name', 'club_league_name', 'country_name', 'attacking_crossing', 'attacking_finishing',
            'attacking_heading_accuracy', 'attacking_short_passing', 'attacking_volleys',
            'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing', 'skill_ball_control',
            'movement_acceleration', 'movement_sprint_speed', 'movement_agility', 'movement_reactions', 'movement_balance',
            'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength', 'power_long_shots',
            'mentality_aggression', 'mentality_interceptions', 'mentality_att_positioning', 
            'mentality_vision', 'mentality_penalties', 'mentality_composure',
            'defending_defensive_awareness', 'defending_standing_tackle', 'defending_sliding_tackle',
            'goalkeeping_gk_diving', 'goalkeeping_gk_handling', 'goalkeeping_gk_kicking', 
            'goalkeeping_gk_positioning', 'goalkeeping_gk_reflexes'
        ]

        file_exists = os.path.isfile(filename)
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            if not file_exists:
                writer.writeheader()
            writer.writerow({k: stats.get(k, "") for k in columns})

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="SoFIFA Player Scraper")
    parser.add_argument(
        "--max-players",
        type=int,
        default=None,
        help="Limit the number of players to scrape"
    )
    parser.add_argument(
        "--player-urls-file",
        default="player_urls.csv",
        help="Path to the CSV file containing player URLs"
    )
    parser.add_argument(
        "--output-file",
        default="player_stats.csv",
        help="Path to the CSV file for saving player stats"
    )
    return parser.parse_args()


async def main():
    """Main function to run the scraper"""
    args = parse_args()
    scraper = SoFIFAScraper(
        player_urls_file=args.player_urls_file,
        output_file=args.output_file
    )
    
    # Load player URLs from CSV file
    print("="*60)
    print("SoFIFA Player Scraper")
    print("="*60)
    scraper.load_player_urls()
    
    # Scrape detailed stats for each player
    print("\n" + "="*60)
    print("Scraping detailed stats for each player")
    print("="*60)
    
    print(f"\nTotal players to scrape: {len(scraper.player_urls)}")
    print("Note: Scraping all players may take a long time.")
    
    # Set to None to scrape all players, or set a number to limit
    if args.max_players:
        print(f"Limiting to first {args.max_players} players...")
    
    await scraper.scrape_player_stats(max_players=args.max_players)
    
    # Print summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETED!")
    print("="*60)
    print(f"Total player URLs loaded: {len(scraper.player_urls)}")
    print(f"Total player stats scraped: {len(scraper.player_stats)}")
    print("\nFile created:")
    print("  - player_stats.csv (detailed stats for all players)")
    
    # Show sample of stats columns
    if scraper.player_stats:
        print(f"\nSample player: {scraper.player_stats[0].get('name', 'Unknown')}")
        print(f"Stats columns: {len(scraper.player_stats[0])} total")
        stat_cols = list(scraper.player_stats[0].keys())
        print(f"First 10 columns: {', '.join(stat_cols[:10])}")


if __name__ == "__main__":
    asyncio.run(main())