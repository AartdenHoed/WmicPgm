using System;
using System.Collections.Generic;
using System.Data;
using System.Data.Entity;
using System.Data.Entity.Infrastructure;
using System.Linq;
using System.Net;
using System.Web;
using System.Web.Mvc;
using ConfigMan;
using System.Diagnostics.Contracts;

namespace ConfigMan.Controllers
{
    public class ComputersController : Controller
    {
        private DbEntities db = new DbEntities();
        private static bool ContractErrorOccurred = false;
        private static string ErrorMessage = " ";

        //
        // GET: Computers
        //
        public ActionResult Index()
        {
            if (ContractErrorOccurred) {
                ContractErrorOccurred = false;
                ViewBag.SympaMsg = ErrorMessage;
                ErrorMessage = " ";
            }
            else {
                ViewBag.SympaMsg = TempData["SympaMsg"];
            } 
            return View(db.Computers.OrderBy(x => x.ComputerName).ToList());
        }

        //
        // GET: Computers/Details/5
        //
        public ActionResult Details(int? id)
        {
            Contract.Requires((id != null) && (id > 0));
            Contract.ContractFailed += (Contract_ContractFailed);

            if (!ContractErrorOccurred) {
                Computer computer = db.Computers.Find(id);
                if (computer == null) {
                    TempData["SympaMsg"] = "*** ERROR *** ID " + id.ToString() + " not found in database.";
                }
                else {
                    return View(computer);
                }
            }
            return RedirectToAction("Index");
        }

        private void Contract_ContractFailed(object sender, ContractFailedEventArgs e) {
            ErrorMessage = "*** ERROR *** Selected computer id is invalid.";
            ContractErrorOccurred = true;
            e.SetHandled();
            return;
        }

        //
        // GET: Computers/Create
        //
        public ActionResult Create()
        {
            return View();
        }

        // POST: Computers/Create
        // To protect from overposting attacks, please enable the specific properties you want to bind to, for 
        // more details see http://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Create([Bind(Include = "ComputerID,ComputerName,ComputerPurchaseDate")] Computer computer)
        {
            if (ModelState.IsValid)
            {
                bool addfailed = false;
                db.Computers.Add(computer);
                try {
                    db.SaveChanges();
                    TempData["SympaMsg"] = computer.ComputerName + " succesfully added."; 
                }
                catch (DbUpdateException) {
                    addfailed = true;
                    ViewBag.SympaMsg = computer.ComputerName + " already exists, use update function.";
                }
                if (addfailed) { return View(); }
                else { return RedirectToAction("Index"); }
            }

            return View(computer);
        }

        //
        // GET: Computers/Edit/5
        //
        public ActionResult Edit(int? id)
        {
            Contract.Requires((id != null) && (id > 0));
            Contract.ContractFailed += (Contract_ContractFailed);

            if (!ContractErrorOccurred) {
                Computer computer = db.Computers.Find(id);
                if (computer == null) {
                    TempData["SympaMsg"] = "*** ERROR *** ID " + id.ToString() + " not found in database.";
                }
                else {
                    computer.ComputerName = computer.ComputerName.Trim();
                    return View(computer);
                }
            }
            return RedirectToAction("Index");

        }

        // POST: Computers/Edit/5
        // To protect from overposting attacks, please enable the specific properties you want to bind to, for 
        // more details see http://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Edit([Bind(Include = "ComputerID,ComputerName,ComputerPurchaseDate")] Computer computer)
        {
            if (ModelState.IsValid)
            {
                db.Entry(computer).State = EntityState.Modified;
                db.SaveChanges();
                TempData["SympaMsg"] = computer.ComputerName + " succesfully updated.";
                return RedirectToAction("Index");
            }
            return View(computer);
        }

        //
        // GET: Computers/Delete/5
        //
        public ActionResult Delete(int? id)
        {
            Contract.Requires((id != null) && (id > 0));
            Contract.ContractFailed += (Contract_ContractFailed);

            if (!ContractErrorOccurred) {
                Computer computer = db.Computers.Find(id);
                if (computer == null) {
                    TempData["SympaMsg"] = "*** ERROR *** ID " + id.ToString() + " not found in database.";
                }
                else {
                    return View(computer);
                }
            }
            return RedirectToAction("Index");

        }
        

        // POST: Computers/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public ActionResult DeleteConfirmed(int id)
        {
            Contract.Requires(id > 0);
            Contract.ContractFailed += (Contract_ContractFailed);
            if (!ContractErrorOccurred) {
                Computer computer = db.Computers.Find(id);
                db.Computers.Remove(computer);
                db.SaveChanges();
                TempData["SympaMsg"] = computer.ComputerName + " succesfully deleted.";
            }
            return RedirectToAction("Index");
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                db.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
