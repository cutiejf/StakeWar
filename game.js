(() => {
  "use strict";

  const startingChips = 10000;
  const maxAutoHands = 50;
  const ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"];
  const suits = ["hearts", "diamonds", "clubs", "spades"];
  const state = {
    chips: startingChips,
    bets: { main: 50, tie: 0, suited: 0 },
    tally: {
      "main_2x": 0, "main_0x": 0, "main_tie": 0,
      "main_2.5x": 0, "main_3.5x": 0, "main_5x": 0, "main_100x": 0,
      side_tie: 0, side_suited: 0, "side_suited+win": 0, wars_lost: 0
    },
    handsPlayed: 0,
    busy: false,
    auto: false
  };

  const $ = (selector) => document.querySelector(selector);
  const delay = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const cardBack = "cards/card_back.png";

  function format(value) {
    return Math.floor(value).toLocaleString("en-US");
  }

  function cardImage(card, className = "playing-card") {
    const img = document.createElement("img");
    const rank = card ? (card.rank.length === 1 && /\d/.test(card.rank) ? `0${card.rank}` : card.rank) : null;
    img.className = className;
    img.src = card ? `cards/card_${card.suit}_${rank}.png` : cardBack;
    img.alt = card ? `${card.rank} of ${card.suit}` : "Face-down card";
    return img;
  }

  function renderCards(container, cards, winner = null, highlightIndex = null) {
    const target = $(container);
    target.replaceChildren(...cards.map((card, index) => {
      const img = cardImage(card);
      if (winner && (highlightIndex === null || index === highlightIndex)) img.classList.add(winner);
      return img;
    }));
  }

  function update() {
    $("#chips").textContent = format(state.chips);
    const profit = state.chips - startingChips;
    $("#profit").textContent = `${profit >= 0 ? "+" : "−"}${format(Math.abs(profit))}`;
    $("#profit").style.color = profit >= 0 ? "#8bd19f" : "#f08a82";

    for (const [key, id] of [["main", "main-bet"], ["tie", "tie-bet"], ["suited", "suited-bet"]]) {
      $(`#${id}`).textContent = format(state.bets[key]);
    }

    const total = state.bets.main + state.bets.tie + state.bets.suited;
    $("#total-bet").textContent = format(total);
    $("#deal-button").disabled = state.busy || state.chips < 50 || state.bets.main < 50 || total > state.chips;
    $("#auto-button").disabled = state.chips < 50 && !state.auto;
    $("#auto-button").classList.toggle("is-active", state.auto);
    $("#auto-button").textContent = state.auto ? "■  STOP AUTO" : "▶  AUTO PLAY";

    document.querySelectorAll("[data-bet][data-step]").forEach((button) => {
      const key = button.dataset.bet;
      const step = Number(button.dataset.step);
      const next = state.bets[key] + step;
      const nextTotal = total + step;
      const minimum = key === "main" ? 50 : 0;
      button.disabled = state.busy || next < minimum || nextTotal > state.chips;
    });

    for (const [key, count] of Object.entries(state.tally)) {
      const cell = document.querySelector(`[data-stat="${key}"]`);
      if (cell) cell.textContent = format(count);
    }
  }

  function setMessage(title, detail, kicker = "HAND RESULT") {
    $("#message").innerHTML = `<span class="message-kicker">${kicker}</span><strong>${title}</strong><span>${detail}</span>`;
  }

  function makeDeck() {
    const deck = ranks.flatMap((rank) => suits.map((suit) => ({ rank, suit })));
    for (let i = deck.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
  }

  function value(card) {
    const faceValues = { J: 11, Q: 12, K: 13, A: 14 };
    return faceValues[card.rank] || Number(card.rank);
  }

  function draw(deck, count = 1) {
    return Array.from({ length: count }, () => deck.pop());
  }

  function addPayout(amount) {
    state.chips += Math.floor(amount);
  }

  async function playHand() {
    if (state.busy || state.chips < 50) return;
    const totalBet = state.bets.main + state.bets.tie + state.bets.suited;
    if (state.bets.main < 50 || totalBet > state.chips) return;

    state.busy = true;
    state.handsPlayed += 1;
    state.chips -= totalBet;
    update();

    const deck = makeDeck();
    const player = draw(deck)[0];
    const house = draw(deck)[0];
    renderCards("#player-cards", [null]);
    renderCards("#house-cards", [null]);
    setMessage("Cards are dealt", "May the higher card win.", "GOOD LUCK");
    await delay(350);
    renderCards("#player-cards", [player]);
    await delay(300);
    renderCards("#house-cards", [house]);
    await delay(350);

    let payout = 0;
    const tieWin = value(player) === value(house) && state.bets.tie > 0;
    const suitedWin = player.suit === house.suit && state.bets.suited > 0;
    if (tieWin) {
      const sidePayout = state.bets.tie * 3;
      payout += sidePayout;
      addPayout(sidePayout);
      state.tally.side_tie += 1;
    }
    if (suitedWin) {
      const sidePayout = state.bets.suited * 3;
      payout += sidePayout;
      addPayout(sidePayout);
      state.tally.side_suited += 1;
    }

    if (value(player) > value(house)) {
      const mainPayout = state.bets.main * 2;
      payout += mainPayout;
      addPayout(mainPayout);
      state.tally["main_2x"] += 1;
      if (suitedWin) {
        const bonus = state.bets.suited * 2;
        payout += bonus;
        addPayout(bonus);
        state.tally["side_suited+win"] += 1;
      }
      renderCards("#player-cards", [player], "is-winner");
      renderCards("#house-cards", [house], "is-loser");
      setMessage("You win!", `${player.rank} beats ${house.rank} · paid ${format(payout)} chips`);
    } else if (value(house) > value(player)) {
      state.tally["main_0x"] += 1;
      renderCards("#player-cards", [player], "is-loser");
      renderCards("#house-cards", [house], "is-winner");
      setMessage("House wins", `${house.rank} beats ${player.rank} · paid ${format(payout)} in side bets`);
    } else {
      state.tally.main_tie += 1;
      renderCards("#player-cards", [player], "is-tie");
      renderCards("#house-cards", [house], "is-tie");
      setMessage("It’s a tie!", "The main bet goes to War.", "TIME FOR WAR");
      await delay(500);
      const warPayout = await playWar(deck);
      payout += warPayout;
    }

    state.busy = false;
    update();
    if (state.chips < 50) {
      state.auto = false;
      setMessage("Game over", "You need at least 50 chips to play again.", "OUT OF CHIPS");
      update();
    }
    return payout;
  }

  async function playWar(deck) {
    const playerCards = draw(deck, 3);
    const houseCards = draw(deck, 3);
    if (playerCards.some((card) => !card) || houseCards.some((card) => !card)) {
      state.tally.wars_lost += 1;
      state.tally["main_0x"] += 1;
      setMessage("Deck exhausted", "The remaining main bet is lost.", "WAR ENDS");
      return 0;
    }

    const shownPlayer = [null, null, null];
    const shownHouse = [null, null, null];
    renderCards("#player-cards", shownPlayer);
    renderCards("#house-cards", shownHouse);
    setMessage("Time for War", "Three cards face down. First higher card wins.", "WAR");
    await delay(350);

    for (let i = 2; i >= 0; i -= 1) {
      shownPlayer[i] = playerCards[i];
      renderCards("#player-cards", shownPlayer);
      await delay(250);
      shownHouse[i] = houseCards[i];
      renderCards("#house-cards", shownHouse);
      await delay(300);
      if (value(playerCards[i]) === value(houseCards[i])) {
        shownPlayer[i] = playerCards[i];
        shownHouse[i] = houseCards[i];
        setMessage("War tie", "Both cards match. Reveal the next pair.", "WAR CONTINUES");
        await delay(350);
        continue;
      }

      if (value(playerCards[i]) > value(houseCards[i])) {
        const multiplier = i === 2 ? 2.5 : i === 1 ? 3.5 : 5;
        const warPayout = Math.floor(state.bets.main * multiplier);
        addPayout(warPayout);
        state.tally[`main_${multiplier}x`] += 1;
        renderCards("#player-cards", shownPlayer, "is-winner", i);
        renderCards("#house-cards", shownHouse, "is-loser", i);
        setMessage("You win the War!", `${playerCards[i].rank} beats ${houseCards[i].rank} · ${multiplier}x pays ${format(warPayout)} chips`);
        return warPayout;
      }

      state.tally.wars_lost += 1;
      state.tally["main_0x"] += 1;
      renderCards("#player-cards", shownPlayer, "is-loser", i);
      renderCards("#house-cards", shownHouse, "is-winner", i);
      setMessage("House wins the War", `${houseCards[i].rank} beats ${playerCards[i].rank} · main bet lost`);
      return 0;
    }

    const jackpot = state.bets.main * 100;
    addPayout(jackpot);
    state.tally["main_100x"] += 1;
    renderCards("#player-cards", playerCards, "is-tie");
    renderCards("#house-cards", houseCards, "is-tie");
    setMessage("Triple War jackpot!", `All three pairs tied · 100x pays ${format(jackpot)} chips`, "JACKPOT");
    return jackpot;
  }

  document.querySelectorAll("[data-bet][data-step]").forEach((button) => {
    button.addEventListener("click", () => {
      const key = button.dataset.bet;
      const step = Number(button.dataset.step);
      const next = state.bets[key] + step;
      const total = state.bets.main + state.bets.tie + state.bets.suited + step;
      if (next < (key === "main" ? 50 : 0) || total > state.chips) return;
      state.bets[key] = next;
      update();
    });
  });

  $("#deal-button").addEventListener("click", async () => {
    await playHand();
  });

  $("#auto-button").addEventListener("click", async () => {
    if (state.auto) {
      state.auto = false;
      update();
      return;
    }
    if (state.busy || state.chips < 50) return;
    state.auto = true;
    const initialHands = state.handsPlayed;
    update();
    while (state.auto && state.chips >= 50 && state.handsPlayed - initialHands < maxAutoHands) {
      const totalBet = state.bets.main + state.bets.tie + state.bets.suited;
      if (state.bets.main < 50 || totalBet > state.chips) break;
      await playHand();
      if (state.auto && state.handsPlayed - initialHands < maxAutoHands) await delay(650);
    }
    state.auto = false;
    update();
  });

  renderCards("#player-cards", [null]);
  renderCards("#house-cards", [null]);
  update();
})();
