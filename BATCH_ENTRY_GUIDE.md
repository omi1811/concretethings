# Batch Entry Methods Guide

## Overview

The Concrete QMS provides three methods for recording concrete batch deliveries, designed to accommodate different site configurations and workflows:

1. **Quick Entry** - Fast, simplified form for sites with external vehicle registers (mandatory default)
2. **Bulk Import** - Excel/CSV upload for batch imports from security registers (optional add-on)
3. **Full Form** - Comprehensive form with all fields including vehicle register details

---

## When to Use Each Method

### Quick Entry ⚡ (Recommended for Most Sites)

**Use When:**
- Security team manages vehicle entry register separately
- Need fast data entry for multiple vehicles
- Focus on quality control data only
- Recording batches during or after pour activities

**Advantages:**
- **30 seconds per batch** vs 2 minutes with full form
- Context retention (vendor, grade, location stay filled)
- Optional pour activity linking
- Focus on QC-relevant data only

**Required Fields:**
- Vehicle Number
- Vendor Name
- Grade
- Quantity (m³)
- Delivery Date & Time

**Optional QC Fields:**
- Slump (mm)
- Temperature (°C)
- Location
- Remarks

**Workflow:**
```
1. QC engineer receives vehicle at site
2. Opens Quick Entry form
3. Enters vehicle number (e.g., MH-01-1234)
4. Vendor/grade auto-filled from last entry
5. Enters quantity
6. Optionally adds slump, temperature
7. Clicks "Save & Continue"
8. Form resets for next vehicle
9. Repeat steps 3-8 for all vehicles
10. Click "Done" when finished
```

---

### Bulk Import 📊 (For Periodic Batch Upload)

**Use When:**
- Security maintains weekly/monthly vehicle register in Excel
- Need to import 10+ batches at once
- Catching up on data entry
- Migrating historical data

**Advantages:**
- **Import 50+ batches in 2 minutes** vs 25+ minutes manual entry
- Template ensures data consistency
- Column validation prevents errors
- Links all batches to pour activity at once

**Required Excel Columns:**
- `vehicleNumber` - Vehicle registration (e.g., MH-01-1234)
- `vendorName` - RMC vendor name (e.g., ABC Concrete)
- `grade` - Concrete grade (M20, M25, M30, etc.)
- `quantity` - Quantity in m³ (e.g., 1.5)

**Optional Excel Columns:**
- `deliveryDate` - Date (YYYY-MM-DD format)
- `deliveryTime` - Time (HH:MM format)
- `slump` - Slump in mm
- `temperature` - Temperature in °C
- `location` - Grid reference or location
- `remarks` - Additional notes

**Workflow:**
```
1. Download Excel template from import page
2. Security team fills vehicle register data
3. QC manager receives Excel file
4. Opens Import page
5. (Optional) Select pour activity to link all batches
6. Upload Excel file
7. System validates columns and data
8. Preview shows first 10 rows
9. Click "Import All Batches"
10. System creates batches and shows summary
11. Download error report if any rows failed
```

**Example Excel Data:**
```
vehicleNumber | vendorName     | grade | quantity | deliveryDate | deliveryTime | slump | temperature
MH-01-1234   | ABC Concrete   | M30   | 1.5      | 2025-11-12  | 10:30       | 100   | 32
MH-02-5678   | ABC Concrete   | M30   | 1.5      | 2025-11-12  | 11:00       | 95    | 33
MH-03-9012   | XYZ RMC        | M40   | 2.0      | 2025-11-12  | 11:45       | 110   | 34
```

---

### Full Form 📝 (Comprehensive Data Entry)

**Use When:**
- QC team manages vehicle entry register
- Need to record complete vehicle register details
- Recording historical batches with full information
- Site requires comprehensive documentation

**Includes All Fields:**
- Vehicle register details (driver, phone, gate times)
- RMC vendor information
- Concrete specifications
- Quality control data
- Location and remarks
- Supporting documents

**Use Cases:**
- Sites where QC team controls gate register
- Detailed documentation requirements
- Audits requiring complete vehicle information
- Projects with integrated vehicle + QC systems

---

## Feature Comparison

| Feature | Quick Entry | Bulk Import | Full Form |
|---------|-------------|-------------|-----------|
| **Time per Batch** | ~30 seconds | ~2 seconds (bulk) | ~2 minutes |
| **Best For** | Daily rapid entry | Weekly batch upload | Complete records |
| **Required Fields** | 6 fields | 4 columns | 15+ fields |
| **Context Retention** | ✅ Yes | N/A | ❌ No |
| **Pour Linking** | ✅ Optional | ✅ Optional | ✅ Optional |
| **Vehicle Register** | ❌ Not included | ❌ Not included | ✅ Included |
| **QC Data** | ✅ Optional | ✅ Optional | ✅ Required |
| **Learning Curve** | Easy | Medium | Complex |
| **Mobile Friendly** | ✅ Yes | ❌ Desktop only | ⚠️ Limited |

---

## Real-World Scenarios

### Scenario 1: Security-Managed Site (Recommended: Quick Entry)

**Situation:**
- Large construction site with dedicated security gate
- Security team maintains vehicle register (paper/Excel)
- QC team focuses on testing and quality
- Average 15-20 concrete deliveries per pour

**Solution: Quick Entry Form**
1. Security logs vehicles in their register (name, time, driver)
2. QC engineer uses Quick Entry during/after pour
3. Links all batches to pour activity
4. Adds QC data (slump, temperature) as available
5. Total time: 7-10 minutes for 20 batches

**Result:**
- ✅ Clear separation of responsibilities
- ✅ Fast data entry workflow
- ✅ Focus on quality control
- ✅ Complete batch tracking

---

### Scenario 2: Weekly Reconciliation (Recommended: Bulk Import)

**Situation:**
- Medium site with mixed concrete suppliers
- Security maintains Excel register daily
- QC manager reviews weekly
- Need to import 40-60 batches per week

**Solution: Bulk Import**
1. Security emails `WeeklyRegister_Nov11-15.xlsx` on Friday
2. QC manager opens Import page
3. Uploads file, validates columns
4. Imports 47 batches in 2 minutes
5. Reviews error report (3 duplicate entries)
6. Manually checks and resolves duplicates

**Result:**
- ✅ Minimal manual entry
- ✅ Data consistency
- ✅ Quick weekly catchup
- ✅ Error detection

---

### Scenario 3: QC-Controlled Gate (Recommended: Full Form)

**Situation:**
- Small site, QC team at gate
- QC engineer records all vehicle details
- Complete documentation required
- 3-5 deliveries per day

**Solution: Full Form**
1. QC engineer at gate when vehicle arrives
2. Records driver details, gate times
3. Takes slump and temperature
4. Documents everything in full form
5. Total time: 2 minutes per batch

**Result:**
- ✅ Complete vehicle register
- ✅ Integrated QC + vehicle data
- ✅ Single point of documentation
- ✅ Audit-ready records

---

## Navigation

### From Batch Register Page
- **Quick Entry** button (primary, blue)
- **Import** button (secondary, outline)
- **Full Form** button (secondary, outline)

### From Quick Entry Page
- **Back** to batch register
- **Full Form** link (if more fields needed)

### From Import Page
- **Back** to batch register
- **Download Template** button

---

## Tips & Best Practices

### Quick Entry Tips
1. **Link to Pour First** - Select pour activity to auto-fill grade and location
2. **Let Context Work** - After first entry, vendor/grade stay filled
3. **Use "Save & Continue"** - Keeps you in the flow
4. **Enter QC Data Later** - Can edit batches to add slump/temp if measured after entry
5. **Mobile Friendly** - Works well on tablets at pour site

### Bulk Import Tips
1. **Download Template First** - Ensures correct column names
2. **Keep Template Format** - Don't rename columns or add extra headers
3. **Use Consistent Vendors** - Exact name match helps with analytics
4. **Date Format** - Use YYYY-MM-DD (e.g., 2025-11-12)
5. **Time Format** - Use 24-hour HH:MM (e.g., 14:30)
6. **Check Errors** - Download error report if some rows fail

### General Tips
1. **Choose One Method** - Don't mix entry methods for same pour
2. **Quick Entry for Real-Time** - Use during pour activity
3. **Import for Catch-Up** - Use for backlog or weekly reconciliation
4. **Full Form for Special Cases** - Use when complete vehicle data required

---

## Troubleshooting

### Quick Entry Issues

**Problem:** Vendor name not retained after save
- **Solution:** Ensure you're using "Save & Continue" button, not "Done"

**Problem:** Pour activity not showing
- **Solution:** Ensure pour status is "in_progress" (not "planned" or "completed")

**Problem:** Can't add slump/temperature
- **Solution:** These are optional fields in "Quality Control" card

---

### Bulk Import Issues

**Problem:** "Invalid file format" error
- **Solution:** Save Excel as .xlsx (not .xls or .csv with wrong encoding)

**Problem:** "Missing required column: vehicleNumber" error
- **Solution:** Ensure column headers exactly match template (case-sensitive)

**Problem:** Some rows imported, others failed
- **Solution:** Check error report for specific row issues (duplicate entries, invalid grades, etc.)

**Problem:** Template download not working
- **Solution:** Check browser popup blocker, try different browser

---

## API Endpoints

For developers integrating with external systems:

### Quick Entry API
```
POST /api/batches/quick-entry
Authorization: Bearer {token}
Content-Type: application/json

{
  "projectId": 1,
  "pourActivityId": 1,  // Optional
  "vehicleNumber": "MH-01-1234",
  "vendorName": "ABC Concrete",
  "grade": "M30",
  "quantityReceived": 1.5,
  "deliveryDate": "2025-11-12",
  "deliveryTime": "10:30",
  "slump": 100,  // Optional
  "temperature": 32,  // Optional
  "location": "Grid A-12",  // Optional
  "remarks": "From security register"  // Optional
}
```

### Bulk Import API
```
POST /api/batches/bulk-import
Authorization: Bearer {token}
Content-Type: multipart/form-data

Form Data:
- file: batches.xlsx (Excel/CSV file)
- projectId: 1
- pourActivityId: 1  // Optional
```

### Template Download API
```
GET /api/batches/import-template?format=xlsx
Authorization: Bearer {token}
```

---

## Support

For questions or issues:
- Check this guide first
- Review pour activity workflow (POUR_ACTIVITY_WORKFLOW.md)
- Contact system administrator
- Report bugs with specific error messages and steps to reproduce

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-12  
**Related Docs:** 
- POUR_ACTIVITY_WORKFLOW.md
- MATERIAL_TESTING_GUIDE.md
- COMPLETE_USER_GUIDE.md
