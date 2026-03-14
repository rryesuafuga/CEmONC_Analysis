###############################################################################
# CEmONC Facility Readiness Assessment - Analysis Script
# Elgon Sub-Region (ELMNS), Uganda
# Data source: KoboToolbox export (CSV or XLSX)
# Author: Raymond R. Wayesu (UVRI / ELCHRI)
# Date: March 2026 (v2 - corrected for KoboToolbox export format)
###############################################################################

# ---- 0. Load packages ----
required_pkgs <- c("tidyverse", "readxl", "janitor", "scales", "writexl")
invisible(lapply(required_pkgs, function(p) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p, repos = "https://cloud.r-project.org")
  library(p, character.only = TRUE)
}))

# ---- 1. Import KoboToolbox export ----
# INSTRUCTIONS:
#   1. In KoboToolbox, go to DATA > Downloads
#   2. Export as XLS or CSV
#   3. Place the exported file in your working directory
#   4. Uncomment ONE of the two lines below and update the filename
#   5. Comment out (or delete) the entire "SIMULATED DATA" section below

# dat_raw <- read_excel("CEmONC_Facility_Readiness_Assessment_-_ELMNS__Elgon_Sub-Region_.xlsx")
# dat_raw <- read_csv("CEmONC_Facility_Readiness_Assessment_-_ELMNS__Elgon_Sub-Region_.csv")

# ---- KoboToolbox column name cleaning ----
# KoboToolbox exports column names with group prefixes separated by "/"
# e.g., "anc_quality/anc_bp/bp_routine_taking" instead of "bp_routine_taking"
# This function strips the group prefixes, keeping only the final field name.

strip_group_prefix <- function(df) {
  names(df) <- sub("^.*/", "", names(df))
  # Handle any duplicate names after stripping (shouldn't happen with good form design)
  if (any(duplicated(names(df)))) {
    warning("Duplicate column names found after stripping group prefixes. Check form design.")
  }
  return(df)
}

# To use with real data, uncomment these two lines:
# dat_raw <- strip_group_prefix(dat_raw)
# dat <- dat_raw  # then skip the SIMULATED DATA section entirely

# ---- SIMULATED DATA (for demonstration - delete when using real data) ----
set.seed(42)
facilities <- c("Budadiri","Buwasa","Muyembe","Bududa","Bufumbo","Mukuju",
                 "Bubulo","Bukwo","Kaproron","Kapchorwa","Kaserem","Namatala",
                 "Bugobero","Masafu General Hospital","Tororo General Hospital",
                 "Mulanda","Nagongera","Bukasakya","Busolwe","Rubongi",
                 "Palisa","Butebo","Kibuku","Budaka","Busiu","Nabiganda","Bulucheke")

teams <- rep(paste0("team", 1:4), length.out = 27)

dat <- tibble(
  facility_name = facilities,
  team_number = teams,
  anc_total_score   = sample(8:18, 27, replace = TRUE),
  anc_total_possible = 18,
  intra_total_score  = sample(12:24, 27, replace = TRUE),
  intra_total_possible = 24,
  theatre_score      = sample(2:7, 27, replace = TRUE),
  theatre_possible   = 7,
  pp_score           = sample(1:5, 27, replace = TRUE),
  pp_possible        = 5,
  oth_score          = sample(1:4, 27, replace = TRUE),
  oth_possible       = 4,
  med_score          = sample(3:8, 27, replace = TRUE),
  med_possible       = 8,
  mpdsr_score        = sample(2:7, 27, replace = TRUE),
  mpdsr_possible     = 7,
  hr_adequate        = sample(1:4, 27, replace = TRUE),
  hr_possible        = 4,
  diag_score         = sample(2:8, 27, replace = TRUE),
  diag_possible      = 8,
  st_score           = sample(1:4, 27, replace = TRUE),
  st_possible        = 4,
  ref_score          = sample(1:5, 27, replace = TRUE),
  ref_possible       = 5,
  lead_score         = sample(1:3, 27, replace = TRUE),
  lead_possible      = 3,
  grand_total_score  = NA_real_,
  grand_total_possible = NA_real_,
  grand_pct          = NA_real_
)
# ---- END SIMULATED DATA ----

# ---- 2. Compute derived variables ----
domain_cols <- c("anc_total_score","intra_total_score","theatre_score","pp_score",
                  "oth_score","med_score","mpdsr_score","hr_adequate",
                  "diag_score","st_score","ref_score","lead_score")
possible_cols <- c("anc_total_possible","intra_total_possible","theatre_possible",
                    "pp_possible","oth_possible","med_possible","mpdsr_possible",
                    "hr_possible","diag_possible","st_possible","ref_possible",
                    "lead_possible")

dat <- dat %>%
  mutate(
    grand_total_score    = rowSums(across(all_of(domain_cols))),
    grand_total_possible = rowSums(across(all_of(possible_cols))),
    grand_pct            = round(grand_total_score / grand_total_possible * 100, 1),
    # Domain percentages
    anc_pct   = round(anc_total_score / anc_total_possible * 100, 1),
    intra_pct = round(intra_total_score / intra_total_possible * 100, 1),
    theatre_pct = round(theatre_score / theatre_possible * 100, 1),
    pp_pct    = round(pp_score / pp_possible * 100, 1),
    oth_pct   = round(oth_score / oth_possible * 100, 1),
    med_pct   = round(med_score / med_possible * 100, 1),
    mpdsr_pct = round(mpdsr_score / mpdsr_possible * 100, 1),
    hr_pct    = round(hr_adequate / hr_possible * 100, 1),
    diag_pct  = round(diag_score / diag_possible * 100, 1),
    st_pct    = round(st_score / st_possible * 100, 1),
    ref_pct   = round(ref_score / ref_possible * 100, 1),
    lead_pct  = round(lead_score / lead_possible * 100, 1),
    # Readiness category (WHO SARA thresholds)
    readiness_cat = case_when(
      grand_pct >= 75 ~ "Good (>=75%)",
      grand_pct >= 50 ~ "Moderate (50-74%)",
      TRUE            ~ "Poor (<50%)"
    ),
    readiness_cat = factor(readiness_cat, 
                           levels = c("Poor (<50%)", "Moderate (50-74%)", "Good (>=75%)"))
  )

# ---- 3. Map facility_name codes to readable labels ----
# KoboToolbox exports the 'name' values from the choices sheet (e.g., "budadiri")
# not the labels (e.g., "Budadiri"). This lookup converts them.
# Only needed for real data — simulated data already uses readable names.

facility_labels <- c(
  budadiri = "Budadiri", buwasa = "Buwasa", muyembe = "Muyembe",
  bududa = "Bududa", bufumbo = "Bufumbo", mukuju = "Mukuju",
  bubulo = "Bubulo", bukwo = "Bukwo", kaproron = "Kaproron",
  kapchorwa = "Kapchorwa", kaserem = "Kaserem", namatala = "Namatala",
  bugobero = "Bugobero", masafu_gh = "Masafu General Hospital",
  tororo_gh = "Tororo General Hospital", mulanda = "Mulanda",
  nagongera = "Nagongera", bukasakya = "Bukasakya", busolwe = "Busolwe",
  rubongi = "Rubongi", palisa = "Palisa", butebo = "Butebo",
  kibuku = "Kibuku", budaka = "Budaka", busiu = "Busiu",
  nabiganda = "Nabiganda", bulucheke = "Bulucheke"
)

# Uncomment the following line when using real KoboToolbox export:
# dat$facility_name <- recode(dat$facility_name, !!!facility_labels)

# ---- 4. Summary statistics ----
cat("\n========== OVERALL READINESS SUMMARY ==========\n")
cat(sprintf("Facilities assessed: %d\n", nrow(dat)))
cat(sprintf("Mean readiness score: %.1f%%\n", mean(dat$grand_pct)))
cat(sprintf("Median readiness score: %.1f%%\n", median(dat$grand_pct)))
cat(sprintf("Range: %.1f%% - %.1f%%\n", min(dat$grand_pct), max(dat$grand_pct)))
cat(sprintf("\nReadiness categories:\n"))
print(table(dat$readiness_cat))

# ---- 5. Domain-level summary ----
domain_summary <- tibble(
  Domain = c("ANC Quality","Intrapartum","Theatre","Postpartum","Others",
             "Medicines","MPDSR","Human Resource","Diagnostics","Stores",
             "Referral","Leadership"),
  Mean_pct = c(mean(dat$anc_pct), mean(dat$intra_pct), mean(dat$theatre_pct),
               mean(dat$pp_pct), mean(dat$oth_pct), mean(dat$med_pct),
               mean(dat$mpdsr_pct), mean(dat$hr_pct), mean(dat$diag_pct),
               mean(dat$st_pct), mean(dat$ref_pct), mean(dat$lead_pct)),
  SD_pct = c(sd(dat$anc_pct), sd(dat$intra_pct), sd(dat$theatre_pct),
             sd(dat$pp_pct), sd(dat$oth_pct), sd(dat$med_pct),
             sd(dat$mpdsr_pct), sd(dat$hr_pct), sd(dat$diag_pct),
             sd(dat$st_pct), sd(dat$ref_pct), sd(dat$lead_pct)),
  Min_pct = c(min(dat$anc_pct), min(dat$intra_pct), min(dat$theatre_pct),
              min(dat$pp_pct), min(dat$oth_pct), min(dat$med_pct),
              min(dat$mpdsr_pct), min(dat$hr_pct), min(dat$diag_pct),
              min(dat$st_pct), min(dat$ref_pct), min(dat$lead_pct)),
  Max_pct = c(max(dat$anc_pct), max(dat$intra_pct), max(dat$theatre_pct),
              max(dat$pp_pct), max(dat$oth_pct), max(dat$med_pct),
              max(dat$mpdsr_pct), max(dat$hr_pct), max(dat$diag_pct),
              max(dat$st_pct), max(dat$ref_pct), max(dat$lead_pct))
) %>%
  mutate(across(where(is.numeric), ~round(., 1))) %>%
  arrange(Mean_pct)

cat("\n========== DOMAIN-LEVEL READINESS ==========\n")
print(domain_summary, n = 12)

# ---- 6. Visualisation 1: Facility ranking (horizontal bar chart) ----
p1 <- dat %>%
  mutate(facility_name = fct_reorder(facility_name, grand_pct)) %>%
  ggplot(aes(x = grand_pct, y = facility_name, fill = readiness_cat)) +
  geom_col(width = 0.7) +
  geom_vline(xintercept = c(50, 75), linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  scale_fill_manual(values = c("Poor (<50%)" = "#D32F2F", 
                                "Moderate (50-74%)" = "#FFA000", 
                                "Good (>=75%)" = "#388E3C"),
                    name = "Readiness") +
  scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 25),
                     labels = function(x) paste0(x, "%")) +
  labs(title = "CEmONC Facility Readiness Scores",
       subtitle = "Elgon Sub-Region, Uganda (27 CEmONC facilities)",
       x = "Overall Readiness Score (%)", y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.major.y = element_blank(),
        legend.position = "bottom",
        plot.title = element_text(face = "bold"))

# ---- 7. Visualisation 2: Domain comparison (bar chart with SD) ----
p2 <- domain_summary %>%
  mutate(Domain = fct_reorder(Domain, Mean_pct)) %>%
  ggplot(aes(x = Mean_pct, y = Domain)) +
  geom_col(fill = "#1565C0", width = 0.6) +
  geom_errorbarh(aes(xmin = pmax(Mean_pct - SD_pct, 0), 
                      xmax = pmin(Mean_pct + SD_pct, 100)),
                 height = 0.3, colour = "grey30") +
  geom_vline(xintercept = c(50, 75), linetype = "dashed", colour = "grey40", linewidth = 0.4) +
  scale_x_continuous(limits = c(0, 100), breaks = seq(0, 100, 25),
                     labels = function(x) paste0(x, "%")) +
  labs(title = "Domain-Level Readiness (Mean +/- SD)",
       subtitle = "Across 27 CEmONC facilities",
       x = "Mean Readiness Score (%)", y = NULL) +
  theme_minimal(base_size = 11) +
  theme(panel.grid.major.y = element_blank(),
        plot.title = element_text(face = "bold"))

# ---- 8. Visualisation 3: Heatmap of facility x domain ----
heat_dat <- dat %>%
  select(facility_name, anc_pct, intra_pct, theatre_pct, pp_pct, 
         oth_pct, med_pct, mpdsr_pct, hr_pct, diag_pct, st_pct, 
         ref_pct, lead_pct) %>%
  pivot_longer(-facility_name, names_to = "domain", values_to = "pct") %>%
  mutate(
    domain = recode(domain,
      anc_pct = "ANC", intra_pct = "Intrapartum", theatre_pct = "Theatre",
      pp_pct = "Postpartum", oth_pct = "Others", med_pct = "Medicines",
      mpdsr_pct = "MPDSR", hr_pct = "HR", diag_pct = "Diagnostics",
      st_pct = "Stores", ref_pct = "Referral", lead_pct = "Leadership"),
    domain = factor(domain, levels = c("ANC","Intrapartum","Theatre","Postpartum",
                                        "Others","Medicines","MPDSR","HR",
                                        "Diagnostics","Stores","Referral","Leadership"))
  )

p3 <- heat_dat %>%
  ggplot(aes(x = domain, y = fct_reorder(facility_name, pct, .fun = mean), fill = pct)) +
  geom_tile(colour = "white", linewidth = 0.3) +
  scale_fill_gradient2(low = "#D32F2F", mid = "#FFA000", high = "#388E3C",
                       midpoint = 60, limits = c(0, 100),
                       name = "Score (%)") +
  labs(title = "Facility x Domain Readiness Heatmap",
       x = NULL, y = NULL) +
  theme_minimal(base_size = 9) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        panel.grid = element_blank(),
        plot.title = element_text(face = "bold"))

# ---- 9. Save outputs ----
ggsave("facility_readiness_ranking.png", p1, width = 10, height = 8, dpi = 300)
ggsave("domain_readiness_bars.png", p2, width = 9, height = 6, dpi = 300)
ggsave("facility_domain_heatmap.png", p3, width = 12, height = 10, dpi = 300)

write_xlsx(list(
  "Facility Scores" = dat %>% 
    select(facility_name, team_number, grand_total_score, grand_total_possible, 
           grand_pct, readiness_cat, anc_pct:lead_pct),
  "Domain Summary" = domain_summary
), "CEmONC_Readiness_Analysis_Report.xlsx")

cat("\n========== OUTPUT FILES ==========\n")
cat("1. facility_readiness_ranking.png\n")
cat("2. domain_readiness_bars.png\n")
cat("3. facility_domain_heatmap.png\n")
cat("4. CEmONC_Readiness_Analysis_Report.xlsx\n")
cat("\nAnalysis complete.\n")
