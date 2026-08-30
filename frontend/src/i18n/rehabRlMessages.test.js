import { describe, expect, it } from "vitest";

import { localizeRehabConditions, rehabText } from "./rehabRlMessages.js";

describe("RehabRL Arabic localization", () => {
  it("localizes workspace and database error copy", () => {
    expect(rehabText("ar", "Rehabilitation planning workspace")).toBe(
      "مساحة تخطيط التأهيل",
    );
    expect(rehabText("ar", "The database is temporarily unavailable.")).toBe(
      "قاعدة البيانات غير متاحة مؤقتًا.",
    );
  });

  it("adds Arabic condition metadata to display and search", () => {
    const [condition] = localizeRehabConditions(
      [
        {
          id: "acl_tear",
          name: "ACL Tear",
          category: "Knee",
          body_region: "Lower limb",
          search_text: "acl tear knee",
        },
      ],
      "ar",
    );

    expect(condition.display_name).toBe("إصابة الرباط الصليبي الأمامي");
    expect(condition.display_category).toBe("الركبة");
    expect(condition.search_text).toContain("إصابة الرباط الصليبي الأمامي");
  });
});
