from mongoengine import connect

from models import Doc, User, Sent
import config


def insert_sample_docs():
    docs = [{
        'title': "Russia steps up legal attack against hunter of Stalin's mass graves",
        'text': "MOSCOW (Reuters) - A Russian historian whose exposure of Soviet leader Josef Stalin’s crimes angered officials was accused on Thursday by state investigators of sexually assaulting his adopted daughter, after having been cleared of similar charges in April. The new accusation was made as Russia hosts the soccer World Cup, an event opposition politicians have accused the authorities of using to try to bury bad news at a time when Human Rights Watch says the country is experiencing its “worst human rights crisis” since the Soviet era.      Some of Russia’s leading cultural figures have said that Yuri Dmitriev is being persecuted because his focus on Stalin’s crimes jars with the Kremlin narrative that Russia must not be ashamed of its past. His real crime, they say, has been dedicating himself to documenting Stalin’s 1937-38 Great Terror, in which nearly 700,000 people were executed, according to conservative official estimates. Dmitriev, 62, found a mass grave with up to 9,000 bodies dating from the period. A European Union spokeswoman on Wednesday said the bloc regarded the case against Dmitriev, which it said had already obliged him to spend 13 months in custody, as “dubious” and expected Russia to drop it. On Thursday, investigators set out new charges against him. Interfax cited Dmitriev’s lawyer, Viktor Anufriev, as saying a court in the northwestern city of Petrozavodsk ordered Dmitriev to be detained for two months. ‘INVENTED’ A court in northwest Russia cleared Dmitriev of child pornography charges involving his adopted daughter in April after a long campaign by human rights activists to free him. However, a higher court in the Karelia region overturned his acquittal on June 14 on the basis of an appeal by state prosecutors and Dmitriev was detained by police again on Wednesday evening. On Thursday, state investigators said they had opened a new criminal case against him, this time alleging sexual assault, a crime that carries a prison sentence of up to 20 years. Investigators said in a statement they would ask a court to remand him in custody later on Thursday while they investigated his alleged crimes which they said happened between 2012 and 2016. Anufriev told Reuters earlier on Thursday that his client denied the new accusations, which he called “invented,” and suggested that investigators had opened the new case to try to show they had not been wrong the first time round. The Investigative Committee of Karelia, whose investigators submitted the original case for prosecution, have previously not responded to Reuters’ questions about whether there was a political side to the case, saying only that they are guided by evidence that they collect. Dmitry Gudkov, an opposition politician who hopes to run in Moscow’s mayoral race later this year, said he thought Dmitriev was being persecuted for his work as a historian. “Who is so bothered about a person who has committed only one ‘offence’ — to investigate the crimes of the Stalin era?” Gudkov asked on Thursday on social media.  “Russia, the legal successor of the USSR.”",
    }, {
        'title': "US STOCKS-Wall St wavers as Amazon buy hits health stocks, banks gain",
        'text': "* Drug stocks tumble after Amazon buys online pharmacy * Amazon’s delivery plans hit FedEx, UPS * U.S. Q1 GDP growth revised down to 2 pct * Starbucks drops as CFO to retire * Indexes up: Dow 0.09 pct; S&P 0.19 pct, Nasdaq 0.25 pct (Updates to early afternoon) By Sruthi Shankar June 28 (Reuters) - U.S. stocks swung between gains and losses on Thursday, as Amazon’s foray into drug retailing whipped the healthcare sector, while a rise in financial stocks for the first time in 14 days cushioned the markets. Amazon.com said it would buy online pharmacy PillPack, a move that will put the online retail giant in direct competition with drugstore chains, drug distributors and pharmacy benefit managers. Walgreens Boots Alliance, already under pressure after its third-quarter earnings report, tumbled 9.4 percent and along with UnitedHealth’s 1.8 percent drop pressured the Dow Jones index. Shares of CVS Health sank 6.6 percent, Rite Aid fell 10.9 percent and Express Scripts was down 1.7 percent. The S&P health sector dropped 0.31 percent, while Amazon gained 1.8 percent. The U.S. economy slowed more than previously estimated in the first quarter, according to Commerce Department data that showed gross domestic product increased at a 2 percent annual rate in the period, from its previous estimate of 2.2 percent. The revision came as an escalating trade dispute between the United States and its major trade partners, including China, Canada and the European Union, kept investors on edge. “Sentiment towards trade has become very negative,” said Tom Essaye, founder of investment research firm Sevens Report. “But if we start to get a better rhetoric on trade, this market is primed to rebound because economic activity remains positive.” At 12:54 p.m. ET the Dow Jones Industrial Average was up 21.24 points, or 0.09 percent, at 24,138.83, the S&P 500 was up 5.02 points, or 0.19 percent, at 2,704.65 and the Nasdaq Composite was up 18.34 points, or 0.25 percent, at 7,463.43. Amazon’s burgeoning reach was not limited to just the health sector. Its plans to entice entrepreneurs to set up their own package-delivery businesses sent shares of United Parcel Service and FedEx skidding more than 2 percent. The stocks drove the S&P industrial index down 0.46 percent. Six of the 11 major S&P sectors were higher — with a 0.66 percent gain in the financial index — boosting the S&P 500 ahead of results from the second round of Federal Reserve’s stress test for banks and lenders. Accenture rose 5.2 percent after the consulting and outsourcing services provider reported quarterly revenue and profit above estimates. Starbucks dropped 4.1 percent after the company said its Chief Financial Officer Scott Maw will retire at the end of November. Declining issues outnumbered advancers for a 1.08-to-1 ratio on the NYSE and for a 1.17-to-1 ratio on the Nasdaq. The S&P index recorded nine new 52-week highs and 23 new lows, while the Nasdaq recorded 28 new highs and 99 new lows. (Reporting by Sruthi Shankar in Bengaluru and Savio D’Souza; Editing by Shounak Dasgupta)",
    }]

    for doc in docs:
        insert_doc(title=doc['title'], text=doc['text'])


def insert_doc(title, text):
    doc = Doc(title=title, text=text)
    doc.save()

    from nltk import sent_tokenize
    for i, text in enumerate(sent_tokenize(doc.text)):
        Sent(index=i, text=text, doc=doc).save()


def insert_sample_user():
    user = User(username='annotator1')
    user.set_password('annotator1')
    user.save()


if __name__ == '__main__':
    connect(**config.Config.MONGODB_SETTINGS)

    insert_sample_docs()
    # insert_sample_user()
