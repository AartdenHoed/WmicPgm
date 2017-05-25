using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace ConfigMan.Controllers {
    public class HomeController : Controller {
        public ActionResult Index() {
            return View();
        }

        public ActionResult About() {
            ViewBag.Message = "Welkom bij SYMPA - gratis HOME computer configuratie management";

            return View();
        }

        public ActionResult Contact() {
            ViewBag.Message = "Dit programma wordt u aangeboden door:";

            return View();
        }
    }
}