# Kiwix Hotspot Pre-Curated Content Packs (for OS only and H1 hotspots)

## **Purpose**
This directory documents and tracks updates for the **pre-curated content packs** used in the Kiwix Hotspot appliance.

---

## **Structure**
Each content pack has its own directory, containing:
- `README.md`: Purpose, audience, user value and list of included ZIM files/resources.
- `CHANGELOG.md`: Versioned changelog, grouped into **Added**, **Removed**, **Changed** and **Fixed** categories.

---
## **Process**
**Additions:**
1. Zim requests: Kiwix gets new zim requests which are then processed on the Recipe Funnel: https://github.com/orgs/openzim/projects/31/views/1
2. Review: Some of them might fit into one of our content packs, which we will evaluate internally
3. Add: We then add them to the relevant content pack, and document the addition in the changelog

**Changes:**
1. Updates: We run zim updates, and have a pipeline where these can be tracked: https://farm.openzim.org/pipeline
2. Once an update has been successfully completed, e.g. for Wikipedia, we will document it in the changelog and include the update in one of our regular releases
3. Smaller changes: In case there is a smaller change, e.g. the name or URL changes slightly but contents remain the same, we may not document the change in the changelog

**Removals**
1. Requests to remove: We may receive a request from the content creator to remove their content from our library
2. We will then remove the content from the content packs and document this in the changelog

**Fixes**
1. Bug reports: We may receive a bug report about specific content
2. We will then fix the issue (if possible) and document this in the changelog
