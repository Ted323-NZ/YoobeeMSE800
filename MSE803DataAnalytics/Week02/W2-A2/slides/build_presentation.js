const fs = require("fs");
const path = require("path");

let PptxGenJS;
try {
  PptxGenJS = require("pptxgenjs");
} catch (error) {
  PptxGenJS = require("/Users/ginoted/Documents/GitHub/output/presentation/clinic-care-final-presentation/node_modules/pptxgenjs");
}

const { imageSizingContain } = require("./pptxgenjs_helpers/image");
const {
  warnIfSlideHasOverlaps,
  warnIfSlideElementsOutOfBounds,
} = require("./pptxgenjs_helpers/layout");

const ROOT = path.resolve(__dirname, "..");
const FIGURES = path.join(ROOT, "figures");
const OUTPUT = path.join(ROOT, "output");
const summary = JSON.parse(
  fs.readFileSync(path.join(OUTPUT, "analysis_summary.json"), "utf8")
);

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Weizhao Tan";
pptx.company = "MSE803 Data Analytics";
pptx.subject = "Week 2 Activity 2 - Beijing Multi-Site Air Quality";
pptx.title = "Beijing Multi-Site Air Quality Insights";
pptx.lang = "en-NZ";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-NZ",
};

const C = {
  ink: "22313F",
  muted: "5B6778",
  bg: "F4F0E8",
  panel: "FFF9F1",
  warm: "9C6644",
  warmSoft: "F1DFCF",
  blue: "3F88C5",
  blueSoft: "D9EAF7",
  olive: "6B705C",
  oliveSoft: "E7E5D8",
  line: "D7CCBC",
  plum: "5F0F40",
};

pptx.defineSlideMaster({
  title: "MASTER",
  background: { color: C.bg },
  objects: [
    {
      rect: {
        x: 0,
        y: 0,
        w: 13.333,
        h: 0.16,
        fill: { color: C.warm },
        line: { color: C.warm },
      },
    },
    {
      line: {
        x: 0.65,
        y: 7.05,
        w: 12,
        h: 0,
        line: { color: C.line, pt: 1 },
      },
    },
    {
      text: {
        text: "MSE803 Data Analytics · Week 2 Activity 2",
        options: {
          x: 0.7,
          y: 7.08,
          w: 6,
          h: 0.16,
          fontFace: "Aptos",
          fontSize: 9,
          color: C.muted,
          margin: 0,
        },
      },
    },
  ],
});

function img(name) {
  return path.join(FIGURES, name);
}

function addSlideTitle(slide, eyebrow, title, subtitle) {
  slide.addText(eyebrow.toUpperCase(), {
    x: 0.75,
    y: 0.42,
    w: 4.5,
    h: 0.18,
    fontFace: "Aptos",
    fontSize: 10,
    bold: true,
    color: C.warm,
    charSpace: 1.4,
    margin: 0,
  });
  slide.addText(title, {
    x: 0.75,
    y: 0.72,
    w: 8.8,
    h: 0.42,
    fontFace: "Aptos Display",
    fontSize: 24,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.75,
      y: 1.18,
      w: 10.8,
      h: 0.26,
      fontFace: "Aptos",
      fontSize: 11,
      color: C.muted,
      margin: 0,
    });
  }
}

function addChip(slide, x, y, w, label, value, fill, lineColor) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.78,
    rectRadius: 0.05,
    fill: { color: fill },
    line: { color: lineColor, pt: 1 },
  });
  slide.addText(label, {
    x: x + 0.12,
    y: y + 0.14,
    w: w - 0.24,
    h: 0.12,
    fontFace: "Aptos",
    fontSize: 9,
    color: C.muted,
    margin: 0,
  });
  slide.addText(String(value), {
    x: x + 0.12,
    y: y + 0.34,
    w: w - 0.24,
    h: 0.2,
    fontFace: "Aptos Display",
    fontSize: 18,
    bold: true,
    color: C.ink,
    margin: 0,
  });
}

function addCard(slide, x, y, w, h, title, body, fill = C.panel) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.05,
    fill: { color: fill },
    line: { color: C.line, pt: 1 },
  });
  slide.addText(title, {
    x: x + 0.16,
    y: y + 0.12,
    w: w - 0.32,
    h: 0.2,
    fontFace: "Aptos Display",
    fontSize: 14,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText(body, {
    x: x + 0.16,
    y: y + 0.4,
    w: w - 0.32,
    h: h - 0.5,
    fontFace: "Aptos",
    fontSize: 10.5,
    color: C.ink,
    margin: 0,
    valign: "top",
    fit: "shrink",
  });
}

function addBullets(slide, items, x, y, w, h, fontSize = 14) {
  const runs = [];
  items.forEach((item) => {
    runs.push({ text: item, options: { bullet: { indent: 14 } } });
  });
  slide.addText(runs, {
    x,
    y,
    w,
    h,
    fontFace: "Aptos",
    fontSize,
    color: C.ink,
    margin: 0.05,
    paraSpaceAfterPt: 6,
    breakLine: true,
    fit: "shrink",
  });
}

function addImagePanel(slide, imagePath, x, y, w, h, caption) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.05,
    fill: { color: "FFFFFF" },
    line: { color: C.line, pt: 1 },
  });
  slide.addImage({
    path: imagePath,
    ...imageSizingContain(imagePath, x + 0.08, y + 0.08, w - 0.16, h - 0.42),
  });
  if (caption) {
    slide.addText(caption, {
      x: x + 0.1,
      y: y + h - 0.22,
      w: w - 0.2,
      h: 0.12,
      fontFace: "Aptos",
      fontSize: 8.5,
      color: C.muted,
      align: "center",
      margin: 0,
    });
  }
}

function addPage(slide, number) {
  slide.addText(String(number), {
    x: 12.35,
    y: 7.08,
    w: 0.3,
    h: 0.16,
    align: "right",
    fontFace: "Aptos",
    fontSize: 9,
    color: C.muted,
    margin: 0,
  });
}

function finishSlide(slide, page) {
  addPage(slide, page);
  warnIfSlideHasOverlaps(slide, pptx);
  warnIfSlideElementsOutOfBounds(slide, pptx);
}

const insights = summary.key_insights;

// Slide 1
{
  const slide = pptx.addSlide("MASTER");
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.75,
    y: 0.7,
    w: 5.3,
    h: 5.4,
    rectRadius: 0.06,
    fill: { color: C.panel },
    line: { color: C.line, pt: 1 },
  });
  slide.addText("Beijing Multi-Site\nAir Quality", {
    x: 1.0,
    y: 1.1,
    w: 4.8,
    h: 1.1,
    fontFace: "Aptos Display",
    fontSize: 28,
    bold: true,
    color: C.ink,
    margin: 0,
  });
  slide.addText("Week 2 Activity 2\nStatistical analysis story", {
    x: 1.0,
    y: 2.45,
    w: 3.6,
    h: 0.7,
    fontFace: "Aptos",
    fontSize: 16,
    color: C.warm,
    bold: true,
    margin: 0,
  });
  slide.addText(
    "This presentation continues Week 2 Activity 1 and turns the statistical analysis into a short insight-led story.",
    {
      x: 1.0,
      y: 3.35,
      w: 4.55,
      h: 0.9,
      fontFace: "Aptos",
      fontSize: 12,
      color: C.ink,
      margin: 0,
    }
  );
  addChip(slide, 1.0, 4.65, 1.45, "Rows", "420,768", C.warmSoft, C.warm);
  addChip(slide, 2.6, 4.65, 1.25, "Stations", "12", C.blueSoft, C.blue);
  addChip(slide, 4.0, 4.65, 1.25, "Tasks", "2-6", C.oliveSoft, C.olive);
  addImagePanel(
    slide,
    img("monthly_pm25_o3.png"),
    6.45,
    0.82,
    6.0,
    5.25,
    "Seasonal contrast between PM2.5 and O3"
  );
  slide.addText("Weizhao Tan · MSE803 Data Analytics", {
    x: 0.98,
    y: 5.7,
    w: 3.6,
    h: 0.2,
    fontFace: "Aptos",
    fontSize: 11,
    color: C.muted,
    margin: 0,
  });
  finishSlide(slide, 1);
}

// Slide 2
{
  const slide = pptx.addSlide("MASTER");
  addSlideTitle(
    slide,
    "Scope",
    "Dataset structure and Task 2-6 workflow",
    "Blackboard task wording was not locally available, so the analysis follows a standard statistical sequence."
  );
  addCard(
    slide,
    0.8,
    1.8,
    4.0,
    2.55,
    "Dataset structure",
    "Outer ZIP: beijing+multi+site+air+quality+data.zip\nNested ZIP: PRSA2017_Data_20130301-20170228.zip\n12 station CSV files\n18 columns per hourly record\nMissing values recorded as NA",
    C.panel
  );
  addCard(
    slide,
    5.1,
    1.8,
    2.0,
    2.55,
    "Task 2",
    "Check missing values and identify data quality risks.",
    C.warmSoft
  );
  addCard(
    slide,
    7.35,
    1.8,
    2.0,
    2.55,
    "Task 3",
    "Summarise the main pollutant and weather variables.",
    C.blueSoft
  );
  addCard(
    slide,
    9.6,
    1.8,
    2.0,
    2.55,
    "Task 4",
    "Find monthly and hourly pollution patterns.",
    C.oliveSoft
  );
  addCard(
    slide,
    5.1,
    4.6,
    2.0,
    1.55,
    "Task 5",
    "Measure pollutant and weather correlations.",
    C.panel
  );
  addCard(
    slide,
    7.35,
    4.6,
    2.0,
    1.55,
    "Task 6",
    "Compare stations and turn results into insights.",
    C.panel
  );
  addCard(
    slide,
    9.6,
    4.6,
    2.0,
    1.55,
    "Outcome",
    "Code, results, PPT, and a short talk script ready for GitHub.",
    C.panel
  );
  finishSlide(slide, 2);
}

// Slide 3
{
  const slide = pptx.addSlide("MASTER");
  addSlideTitle(
    slide,
    "Quality",
    "Task 2 and Task 3: data quality and descriptive statistics",
    "The first step was checking which variables were most incomplete before interpreting the averages."
  );
  addImagePanel(
    slide,
    img("missing_rate_by_column.png"),
    0.8,
    1.85,
    6.2,
    4.7,
    "Missing values are concentrated in pollutant variables, not the date fields."
  );
  addBullets(
    slide,
    [
      `CO had the highest missing rate at ${insights.highest_missing_rate_pct.toFixed(2)}%.`,
      "The missing-value pattern is small enough to continue with descriptive analysis, but it should be acknowledged.",
      "Average PM2.5 was 79.79 and average PM10 was 104.60, showing a generally polluted dataset.",
      "The median values are lower than the means for several pollutants, which suggests right-skewed pollution spikes.",
    ],
    7.35,
    2.0,
    5.1,
    2.6,
    14
  );
  addCard(
    slide,
    7.35,
    5.0,
    2.4,
    1.15,
    "PM2.5 mean",
    "79.79",
    C.warmSoft
  );
  addCard(
    slide,
    10.0,
    5.0,
    2.4,
    1.15,
    "PM10 mean",
    "104.60",
    C.blueSoft
  );
  finishSlide(slide, 3);
}

// Slide 4
{
  const slide = pptx.addSlide("MASTER");
  addSlideTitle(
    slide,
    "Seasonality",
    "Task 4: monthly pollution patterns tell the main story",
    "The data shows a strong seasonal contrast: PM2.5 is worst in winter while O3 rises in summer."
  );
  addImagePanel(
    slide,
    img("monthly_pm25_o3.png"),
    0.8,
    1.85,
    7.2,
    4.8,
    "December is the PM2.5 peak month and July is the O3 peak month."
  );
  addCard(
    slide,
    8.35,
    2.0,
    3.8,
    1.15,
    "Peak PM2.5 month",
    `${insights.peak_pm25_month} · ${insights.peak_pm25_month_value.toFixed(2)}`,
    C.warmSoft
  );
  addCard(
    slide,
    8.35,
    3.4,
    3.8,
    1.15,
    "Peak O3 month",
    `${insights.peak_o3_month} · ${insights.peak_o3_month_value.toFixed(2)}`,
    C.blueSoft
  );
  addBullets(
    slide,
    [
      "Cold-season PM2.5 suggests heavier particulate pollution in late autumn and winter.",
      "Warm-season O3 suggests stronger photochemical activity during summer.",
      "This matters because one single mitigation strategy will not work equally well for all pollutants.",
    ],
    8.35,
    4.95,
    4.2,
    1.4,
    13
  );
  finishSlide(slide, 4);
}

// Slide 5
{
  const slide = pptx.addSlide("MASTER");
  addSlideTitle(
    slide,
    "Patterns",
    "Task 4 and Task 5: hourly cycle and pollutant relationships",
    "Daily timing and pairwise correlations help explain which variables move together."
  );
  addImagePanel(
    slide,
    img("hourly_pm25_o3.png"),
    0.8,
    1.9,
    5.8,
    4.6,
    `PM2.5 peaks at ${insights.peak_pm25_hour}:00 while O3 peaks at ${insights.peak_o3_hour}:00.`
  );
  addImagePanel(
    slide,
    img("correlation_heatmap.png"),
    6.95,
    1.9,
    5.45,
    4.6,
    "PM2.5 is strongly linked to PM10 and moderately opposed to wind speed."
  );
  slide.addText(
    `PM2.5 strongest positive correlation: ${insights.pm25_strongest_positive_correlation_column} (${insights.pm25_strongest_positive_correlation_value.toFixed(
      2
    )})`,
    {
      x: 0.95,
      y: 6.68,
      w: 5.6,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 10.5,
      color: C.ink,
      margin: 0,
    }
  );
  slide.addText(
    `PM2.5 strongest negative correlation: ${insights.pm25_strongest_negative_correlation_column} (${insights.pm25_strongest_negative_correlation_value.toFixed(
      2
    )})`,
    {
      x: 7.08,
      y: 6.68,
      w: 5.0,
      h: 0.18,
      fontFace: "Aptos",
      fontSize: 10.5,
      color: C.ink,
      margin: 0,
    }
  );
  finishSlide(slide, 5);
}

// Slide 6
{
  const slide = pptx.addSlide("MASTER");
  addSlideTitle(
    slide,
    "Stations",
    "Task 6: station comparison and final interpretation",
    "Comparing station averages shows where particulate pollution was consistently higher across the whole dataset."
  );
  addImagePanel(
    slide,
    img("station_pm25_ranking.png"),
    0.8,
    1.9,
    6.2,
    4.8,
    "Dongsi has the highest average PM2.5 and Dingling the lowest."
  );
  addBullets(
    slide,
    [
      `${insights.highest_pm25_station} had the highest average PM2.5 at ${insights.highest_pm25_value.toFixed(2)}.`,
      `${insights.lowest_pm25_station} had the lowest average PM2.5 at ${insights.lowest_pm25_value.toFixed(2)}.`,
      "The combined evidence supports a story of winter particulate pollution, summer ozone peaks, and cleaner conditions when wind speed is stronger.",
      "This gives a clear presentation narrative for a short 3-minute explanation.",
    ],
    7.35,
    2.0,
    5.0,
    2.6,
    14
  );
  addCard(
    slide,
    7.35,
    5.0,
    5.0,
    1.15,
    "GitHub folder",
    "https://github.com/Ted323-NZ/YoobeeMSE800/tree/codex/mse803-week02-w2-a2/MSE803DataAnalytics/Week02/W2-A2",
    C.oliveSoft
  );
  addCard(
    slide,
    7.35,
    6.25,
    5.0,
    0.55,
    "Deliverables",
    "analysis code · result tables · figures · PPT · talk script",
    C.panel
  );
  finishSlide(slide, 6);
}

const out = path.join(ROOT, "output", "beijing_air_quality_insights_week2_activity2.pptx");
pptx
  .writeFile({ fileName: out })
  .then(() => {
    console.log(`Wrote ${out}`);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
