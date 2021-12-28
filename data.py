server = "15"

urls = {
    "main": "https://www.omegle.com/",
    "start": 'https://front'+server+'.omegle.com/start?caps=recaptcha2,t&firstevents=1&spid=&randid=BKHDLXDX&topics={TOPICS}&lang={LANG}',
    "event": 'https://front'+server+'.omegle.com/events',
    "disconnect": 'https://front'+server+'.omegle.com/disconnect',
    "send": 'https://front'+server+'.omegle.com/send',
    "typing": 'https://front'+server+'.omegle.com/typing',
    "events": 'https://front'+server+'.omegle.com/events',
    "stoptyping": 'https://front'+server+'.omegle.com/stoppedtyping'
}

header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Accept": "application/json",
    "Accept-Language": "it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-type": "application/x-www-form-urlencoded; charset=utf-8",
    "Content-Length": "0",
    "Origin": "https://www.omegle.com",
    "Connection": "keep-alive",
    "Referer": "https://www.omegle.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers"
}
